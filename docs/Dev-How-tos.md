## Setting up GPG key for signing commits

See https://docs.github.com/en/github/authenticating-to-github/managing-commit-signature-verification/signing-commits
and https://docs.github.com/en/github/authenticating-to-github/managing-commit-signature-verification/telling-git-about-your-signing-key

TEST


Potentially quicker version (of above) that worked on my Mac 
(it did not cache my gpg key password, so maybe it doesn't work - follow above instructions)

```
git config --global commit.gpgsign true
curl https://releases.gpgtools.org/GPG_Suite-2021.1_105.dmg -o GPG_Suite.dmg
open GPG_Suite.dmg
gpg --list-secret-keys --keyid-format=long
```
From last command stdout: 

```
/Users/hubot/.gnupg/secring.gpg
------------------------------------
sec 4096R/3AA5C34371567BD2 2016-03-10 [expires: 2017-03-10]
uid Hubot
ssb 4096R/42B317FD4BA89E7A 2016-03-10
```

Get the key id (e.g 3AA5C34371567BD2) : 
```
git config user.signingkey 3AA5C34371567BD2
```
