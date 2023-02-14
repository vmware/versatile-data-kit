/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.authorization.webhook;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.io.*;

public class AuthorizationBodyTest {

  private AuthorizationBody authzBody;

  @BeforeEach
  public void setUp() {
    authzBody = new AuthorizationBody();
    authzBody.setRequestedHttpPath("/data-jobs");
    authzBody.setRequestedHttpVerb("POST");
    authzBody.setRequestedPermission("write");
    authzBody.setRequestedResourceId("");
    authzBody.setRequesterUserId("auserov");
    authzBody.setRequestedResourceTeam("example-team");
    authzBody.setRequestedResourceName("data-job");
    authzBody.setRequestedResourceNewTeam("example-team");
  }

  @Test
  public void testParseJsonObjectNoIdTeam() throws IOException, ClassNotFoundException {
    byte[] serialized1 = serialize(authzBody);
    byte[] serialized2 = serialize(authzBody);

    Object deserialized1 = deserialize(serialized1);
    Object deserialized2 = deserialize(serialized2);
    Assertions.assertEquals(deserialized1, deserialized2);
    Assertions.assertEquals(authzBody, deserialized1);
    Assertions.assertEquals(authzBody, deserialized2);
  }

  @Test
  public void testVerifyJsonString() {
    String expectedJson =
        "{\"requester_user_id\":\"auserov\","
            + "\"requested_resource_team\":\"example-team\","
            + "\"requested_resource_name\":\"data-job\","
            + "\"requested_resource_id\":\"\","
            + "\"requested_http_path\":\"/data-jobs\","
            + "\"requested_http_verb\":\"POST\","
            + "\"requested_resource_new_team\":\"example-team\","
            + "\"requested_permission\":\"write\"}";

    Assertions.assertEquals(authzBody.toString(), expectedJson);
  }

  private static byte[] serialize(Object object) throws IOException {
    ByteArrayOutputStream arrayOutputStream = new ByteArrayOutputStream();
    ObjectOutputStream objectOutputStream = new ObjectOutputStream(arrayOutputStream);
    objectOutputStream.writeObject(object);
    return arrayOutputStream.toByteArray();
  }

  private static Object deserialize(byte[] bytes) throws IOException, ClassNotFoundException {
    ByteArrayInputStream arrayOutputStream = new ByteArrayInputStream(bytes);
    ObjectInputStream objectOutputStream = new ObjectInputStream(arrayOutputStream);
    return objectOutputStream.readObject();
  }
}
