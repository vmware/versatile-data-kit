# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import datetime
import secrets

from minikerberos import logger
from minikerberos.aioclient import AIOKerberosClient
from minikerberos.protocol.asn1_structs import AS_REQ
from minikerberos.protocol.asn1_structs import EncASRepPart
from minikerberos.protocol.asn1_structs import EncTGSRepPart
from minikerberos.protocol.asn1_structs import KDC_REQ_BODY
from minikerberos.protocol.asn1_structs import KDCOptions
from minikerberos.protocol.asn1_structs import krb5_pvno
from minikerberos.protocol.asn1_structs import PA_PAC_REQUEST
from minikerberos.protocol.asn1_structs import PADATA_TYPE
from minikerberos.protocol.asn1_structs import PrincipalName
from minikerberos.protocol.constants import EncryptionType
from minikerberos.protocol.constants import MESSAGE_TYPE
from minikerberos.protocol.constants import NAME_TYPE
from minikerberos.protocol.encryption import _enctype_table
from minikerberos.protocol.encryption import Key
from minikerberos.protocol.errors import KerberosError
from minikerberos.protocol.errors import KerberosErrorCode


class VdkAioKerberosClient(AIOKerberosClient):
    """
    Implementation is based on minikerberos, patched code is marked with a comment.
    """

    async def get_TGT(
        self,
        override_etype=None,
        decrypt_tgt=True,
        kdcopts=["forwardable", "renewable", "proxiable"],
    ):
        """
        decrypt_tgt: used for asreproast attacks
        Steps performed:
            1. Send and empty (no encrypted timestamp) AS_REQ with all the encryption types we support
            2. Depending on the response (either error or AS_REP with TGT) we either send another AS_REQ with the encrypted data or return the TGT (or fail miserably)
            3. PROFIT
        """

        # first, let's check if CCACHE has the correct ticket already
        _, err = self.tgt_from_ccache(override_etype)
        if err is None:
            return

        logger.debug("Generating initial TGT without authentication data")
        now = datetime.datetime.now(datetime.timezone.utc)
        kdc_req_body = {}
        kdc_req_body["kdc-options"] = KDCOptions(set(kdcopts))
        kdc_req_body["cname"] = PrincipalName(
            {
                "name-type": NAME_TYPE.PRINCIPAL.value,
                "name-string": [self.usercreds.username],
            }
        )
        kdc_req_body["realm"] = self.usercreds.domain.upper()
        kdc_req_body["sname"] = PrincipalName(
            {
                "name-type": NAME_TYPE.PRINCIPAL.value,
                "name-string": ["krbtgt", self.usercreds.domain.upper()],
            }
        )
        kdc_req_body["till"] = (now + datetime.timedelta(days=1)).replace(microsecond=0)
        kdc_req_body["rtime"] = (now + datetime.timedelta(days=1)).replace(
            microsecond=0
        )
        kdc_req_body["nonce"] = secrets.randbits(31)
        if override_etype is None:
            kdc_req_body["etype"] = self.usercreds.get_supported_enctypes()
        else:
            kdc_req_body["etype"] = override_etype

        pa_data_1 = {}
        pa_data_1["padata-type"] = int(PADATA_TYPE("PA-PAC-REQUEST"))
        pa_data_1["padata-value"] = PA_PAC_REQUEST({"include-pac": True}).dump()

        kdc_req = {}
        kdc_req["pvno"] = krb5_pvno
        kdc_req["msg-type"] = MESSAGE_TYPE.KRB_AS_REQ.value
        kdc_req["padata"] = [pa_data_1]
        kdc_req["req-body"] = KDC_REQ_BODY(kdc_req_body)

        req = AS_REQ(kdc_req)

        logger.debug("Sending initial TGT to %s" % self.ksoc.get_addr_str())
        rep = await self.ksoc.sendrecv(req.dump())

        if rep.name != "KRB_ERROR":
            # user can do kerberos auth without preauthentication!
            self.kerberos_TGT = rep.native

            # if we want to roast the asrep (tgt rep) part then we dont even have the proper keys to decrypt
            # so we just return, the asrep can be extracted from this object anyhow
            if decrypt_tgt == False:
                return

            self.kerberos_cipher_type = kdc_req_body["etype"][
                0
            ]  # patched: retrieve first encryption type supported
            self.kerberos_cipher = _enctype_table[self.kerberos_cipher_type]
            self.kerberos_key = Key(
                self.kerberos_cipher.enctype,
                self.usercreds.get_key_for_enctype(
                    EncryptionType(self.kerberos_cipher_type)
                ),
            )

        else:
            if (
                rep.native["error-code"]
                != KerberosErrorCode.KDC_ERR_PREAUTH_REQUIRED.value
            ):
                raise KerberosError(rep)
            rep = rep.native
            logger.debug("Got reply from server, asikg to provide auth data")
            supported_encryption_method = self.select_preferred_encryption_method(rep)

            rep = await self.do_preauth(supported_encryption_method)
            logger.debug("Got valid TGT response from server")
            rep = rep.native
            self.kerberos_TGT = rep

        if self.usercreds.certificate is not None:
            (
                self.kerberos_TGT_encpart,
                self.kerberos_session_key,
                self.kerberos_cipher,
            ) = self.decrypt_asrep_cert(rep)
            self.kerberos_cipher_type = supported_encryption_method.value

            self.ccache.add_tgt(
                self.kerberos_TGT, self.kerberos_TGT_encpart, override_pp=True
            )
            logger.debug("Got valid TGT")
            return

        else:
            cipherText = self.kerberos_TGT["enc-part"][
                "cipher"
            ]  # patched: correct ciphertext lookup
            temp = self.kerberos_cipher.decrypt(self.kerberos_key, 3, cipherText)

            try:
                self.kerberos_TGT_encpart = EncASRepPart.load(temp).native
            except Exception as e:
                logger.debug("EncAsRepPart load failed, is this linux?")
                try:
                    self.kerberos_TGT_encpart = EncTGSRepPart.load(temp).native
                except Exception as e:
                    logger.error("Failed to load decrypted part of the reply!")
                    raise e

            self.kerberos_session_key = Key(
                self.kerberos_cipher.enctype,
                self.kerberos_TGT_encpart["key"]["keyvalue"],
            )
            self.ccache.add_tgt(
                self.kerberos_TGT, self.kerberos_TGT_encpart, override_pp=True
            )
            logger.debug("Got valid TGT")

            return
