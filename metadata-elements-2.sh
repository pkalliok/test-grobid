#!/bin/bash

python3 metadata_elements.py "$@" |
sort -u |
cut -d' ' -f2- |
sort | uniq -c  |
sed 's#{http[^}]*}##g' |
egrep -vw 'appInfo|application|availability|biblStruct|encodingDesc|fileDesc|imprint|monogr|profileDesc|publicationStmt|ref|sourceDesc|TEI|teiHeader|title/level|titleStmt|key|unit|type|address|addrLine|country|p|postBox|abstract/lang|analytic|persName' |
sort -rn |
sed 's#text/lang#kieli#;s#title#nimeke#;s#author#tekijä#;s#surname#tekijän sukunimi#;s#forename#tekijän etunimi#;s#note#tunnistamaton tieto#;s#date/when#julkaisupäivä (määr.)#;s#date#julkaisupäivä#;s#orgName#tekijäorganisaatio#;s#affiliation#tekijän taustaorg.#;s#abstract#tiivistelmä#;s#roleName#roolitermi#;s#meeting#julkaisupaikka#;s#biblScope#numero sarjassa#'

