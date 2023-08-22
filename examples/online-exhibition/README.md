# Online Exhibition
The objective of this scenario is to ingest and process in VDK Vincent Van Gogh's paintings available in [Europeana](https://www.europeana.eu/en), a well-known European aggregator for Cultural Heritage. Europeana provides all the Cultural Heritage objects through its public [REST API](https://pro.europeana.eu/page/intro#access).

This example provides the complete code to perform the following tasks:

* Data Ingestion from REST API
* Data Processing
* Data Publication in form of an innteractive App

The directory is organized as follows:

* online-exhibition - contains jobs
* view.py - contains the code to generate the app

## Scenario
An association of emerging painters would like to set up an online exhibition on Vincent Van Gogh, a well-known Dutch post-impressionist painter. Within the online exhibition, the association would like to reserve a special section for paintings from the Rijksmuseum in Amsterdam.

The paintings to be included in the exhibition are available on [Europeana](https://www.europeana.eu/en), a well-known European aggregator of the cultural heritage of various kinds. Europeana provides more than 700 works whose author is Vincent Van Gogh.

## Data Source

Europeana provides a [REST API](https://pro.europeana.eu/page/intro#access) for accessing resources. For each resource, various information is available, including the organization that provided the resource.

For each record, the REST API provides the following information:
* completeness
* country,
* dataProvider,
* dcCreator,
* dcCreatorLangAware,
* dcTitleLangAware,
* edmDatasetName
* edmIsShownBy
* edmPreview
* edmTimespanLabel
* edmTimespanLabelLangAware
* europeanaCollectionName
* europeanaCompleteness
* guid
* id
* index
* language
* link
* previewNoDistribute
* provider
* rights
* score
* timestamp
* timestamp_created
* timestamp_created_epoch
* timestamp_update
* timestamp_update_epoch
* title
* type
* ugc

The following JSON shows a record extract returned by the API:

```
[{
    completeness: 10,
    country: ["Belgium"],
    dataProvider: ["Catholic University of Leuven"],
    dcCreator: ["http://data.europeana.eu/agent/base/59832",
    "Vincent van Gogh"],
    dcCreatorLangAware: {
        def: ["http://data.europeana.eu/agent/base/59832"],
        en:  ["Vincent van Gogh"]
    },
    dcDescription:
        ["KU Leuven. Glasdia’s kunstgeschiedenis. Université de Louvain, tussen 1839 en 1939. Fotograaf onbekend. Toegevoegde informatie op dia. Stroming/Stijl: Postimpressionisme. Creatie/Bouw: 1889. Techniek/Materiaal: Olieverf op doek. Huidige locatie: Nederland, Otterlo, Kröller-Müller Museum. EuroPhot. Kunstgeschiedenis. 19de eeuw. Schilderkunst. Portret. EuroPhot. Art history. 19th century. Paintings. Portrait."],
        ...
}]
```

The access point to the REST API is available at the following link:
```
https://api.europeana.eu/record/v2/search.json
```
It is necessary to register for free to obtain an API key.


## Requirements

To run this example, you need:

* Versatile Data Kit
* Trino DB
* Versatile Data Kit plugin for Trino
* Versatile Data Kit Server
* Europeana API key
* Streamlit

For more details on how to install Versatile Data Kit, Trino DB, Streamlit and Versatile Data Kit plugin for Trino, please refer to [this link](https://github.com/vmware/versatile-data-kit/tree/main/examples/life-expectancy).

### Versatile Data Kit Server
In this example, we install the Versatile Data Kit (VDK) server locally.
The VDK server requires the following prerequisites:
* helm
* docker
* kind

We can install the Versatile Data Kit Server through the following command:
```
vdk server --install
```
For more information on how to install the VDK server, you can refer to the [Official Documentation](https://github.com/vmware/versatile-data-kit/wiki/Installation#install-locally)

### Europeana API key
We can obtain a Europeana API key by registering to [this link](https://pro.europeana.eu/page/get-api). We should complete a form that requests our email. Once we submit the form, the API key is sent by email.

### Other Requirements
This example also requires the following Python libraries, which are included in the requirement.txt file:
```
configparser
pandas
requests
```

## Configuration
The following example uses the same configuration as the [Life Expectancy](https://github.com/vmware/versatile-data-kit/tree/main/examples/life-expectancy) scenario, with the only difference on the trino schama used by the Versatile Data Kit configuration file:
```
trino_schema = online-exhibition
```

### Europeana API key
We can add the Europeana API key as a vdk property as follows:
```
vdk properties --set api_key YOUR_API_KEY
```

Then, we will access it in data job with the `job_input.get_property()` method.

## Data Ingestion
Data Ingestion uploads in the database output of the call to the Europeana REST API, defined in the Data Source section. Data Ingestion is performed through the following steps:

* delete the existing table (if any)
* create a new table
* ingest table values directly from the REST API.

To access the Europeana REST API, this example requires an active Internet connection to work properly.

Jobs 01-03 are devoted to Data Ingestion. The output of the REST API is imported in table called `assets`, that contains raw values. For example, a column could contain a JSON.

The following table shows an example of the `assets` table:
|completeness|country    |dataprovider                                                                     |dccreator                                                                       |dccreatorlangaware                                                                       |dctitlelangaware                                             |edmdatasetname                   |edmisshownby                                   |edmpreview                                                                                                               |edmtimespanlabel|edmtimespanlabellangaware|europeanacollectionname          |europeanacompleteness|guid                                                                                                                        |id                                        |index|language|link                                                                                          |previewnodistribute|provider                  |rights                                        |score    |timestamp    |timestamp_created       |timestamp_created_epoch|timestamp_update        |timestamp_update_epoch|title                                                |type |ugc    |
|------------|-----------|---------------------------------------------------------------------------------|--------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|-------------------------------------------------------------|---------------------------------|-----------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|----------------|-------------------------|---------------------------------|---------------------|----------------------------------------------------------------------------------------------------------------------------|------------------------------------------|-----|--------|----------------------------------------------------------------------------------------------|-------------------|--------------------------|----------------------------------------------|---------|-------------|------------------------|-----------------------|------------------------|----------------------|-----------------------------------------------------|-----|-------|
|6           |['Germany']|['Deutsches Dokumentationszentrum für Kunstgeschichte - Bildarchiv Foto Marburg']|['https://d-nb.info/gnd/118540416', 'http://data.europeana.eu/agent/base/59832']|{'def': ['https://d-nb.info/gnd/118540416', 'http://data.europeana.eu/agent/base/59832']}|{'de': ['Olivenbäume vor den Alpillen / Olivenhain']}        |['199_DDB_BildarchivFotoMarburg']|['http://www.bildindex.de/bilder/d/fm606298']  |['https://api.europeana.eu/thumbnail/v2/url.json?uri=http%3A%2F%2Fwww.bildindex.de%2Fbilder%2Fd%2Ffm606298&type=IMAGE']  |nan             |nan                      |['199_DDB_BildarchivFotoMarburg']|6                    |https://www.europeana.eu/item/199/item_TRRC3SE5ZVBRN23GGTDXJQHFHCEU2MBH?utm_source=api&utm_medium=api&utm_campaign=ckwoetann|/199/item_TRRC3SE5ZVBRN23GGTDXJQHFHCEU2MBH|0    |['de']  |https://api.europeana.eu/record/199/item_TRRC3SE5ZVBRN23GGTDXJQHFHCEU2MBH.json?wskey=ckwoetann|0                  |['German Digital Library']|['http://rightsstatements.org/vocab/InC/1.0/']|29.144974|1643639779258|2019-04-16T11:48:44.409Z|1555415324409          |2022-01-31T11:04:15.728Z|1643627055728         |['Olivenbäume vor den Alpillen / Olivenhain']        |IMAGE|[False]|
|6           |['Germany']|['Deutsches Dokumentationszentrum für Kunstgeschichte - Bildarchiv Foto Marburg']|['https://d-nb.info/gnd/118540416', 'http://data.europeana.eu/agent/base/59832']|{'def': ['https://d-nb.info/gnd/118540416', 'http://data.europeana.eu/agent/base/59832']}|{'de': ['Straße mit Telegraphenmast und Kran']}              |['199_DDB_BildarchivFotoMarburg']|['http://www.bildindex.de/bilder/d/nl00022g10']|['https://api.europeana.eu/thumbnail/v2/url.json?uri=http%3A%2F%2Fwww.bildindex.de%2Fbilder%2Fd%2Fnl00022g10&type=IMAGE']|nan             |nan                      |['199_DDB_BildarchivFotoMarburg']|6                    |https://www.europeana.eu/item/199/item_V5X2YM7XNWZPFP3WXPSH6UMSAZ3R3W2A?utm_source=api&utm_medium=api&utm_campaign=ckwoetann|/199/item_V5X2YM7XNWZPFP3WXPSH6UMSAZ3R3W2A|0    |['de']  |https://api.europeana.eu/record/199/item_V5X2YM7XNWZPFP3WXPSH6UMSAZ3R3W2A.json?wskey=ckwoetann|0                  |['German Digital Library']|['http://rightsstatements.org/vocab/InC/1.0/']|29.144974|1643643461472|2019-04-16T14:03:08.283Z|1555423388283          |2022-01-31T11:04:15.728Z|1643627055728         |['Straße mit Telegraphenmast und Kran']              |IMAGE|[False]|
|6           |['Germany']|['Deutsches Dokumentationszentrum für Kunstgeschichte - Bildarchiv Foto Marburg']|['http://data.europeana.eu/agent/base/59832', 'https://d-nb.info/gnd/118540416']|{'def': ['http://data.europeana.eu/agent/base/59832', 'https://d-nb.info/gnd/118540416']}|{'de': ['Alter Mann seinen Kopf in den Händen haltend']}     |['199_DDB_BildarchivFotoMarburg']|['http://www.bildindex.de/bilder/d/nl00022d12']|['https://api.europeana.eu/thumbnail/v2/url.json?uri=http%3A%2F%2Fwww.bildindex.de%2Fbilder%2Fd%2Fnl00022d12&type=IMAGE']|nan             |nan                      |['199_DDB_BildarchivFotoMarburg']|6                    |https://www.europeana.eu/item/199/item_XO5QORU6LU6SDSZWX3IPZRWP3QOASFSK?utm_source=api&utm_medium=api&utm_campaign=ckwoetann|/199/item_XO5QORU6LU6SDSZWX3IPZRWP3QOASFSK|0    |['de']  |https://api.europeana.eu/record/199/item_XO5QORU6LU6SDSZWX3IPZRWP3QOASFSK.json?wskey=ckwoetann|0                  |['German Digital Library']|['http://rightsstatements.org/vocab/InC/1.0/']|29.144974|1643632823575|2019-04-16T11:20:03.731Z|1555413603731          |2022-01-31T11:04:15.728Z|1643627055728         |['Alter Mann seinen Kopf in den Händen haltend']     |IMAGE|[False]|
|6           |['Germany']|['Deutsches Dokumentationszentrum für Kunstgeschichte - Bildarchiv Foto Marburg']|['http://data.europeana.eu/agent/base/59832', 'https://d-nb.info/gnd/118540416']|{'def': ['http://data.europeana.eu/agent/base/59832', 'https://d-nb.info/gnd/118540416']}|{'de': ['Feld mit Pflug und Egge']}                          |['199_DDB_BildarchivFotoMarburg']|['http://www.bildindex.de/bilder/d/fmc663092'] |['https://api.europeana.eu/thumbnail/v2/url.json?uri=http%3A%2F%2Fwww.bildindex.de%2Fbilder%2Fd%2Ffmc663092&type=IMAGE'] |nan             |nan                      |['199_DDB_BildarchivFotoMarburg']|6                    |https://www.europeana.eu/item/199/item_Y4UVK7V7IXHND3PJ4RUGGYRM7XYSUMYH?utm_source=api&utm_medium=api&utm_campaign=ckwoetann|/199/item_Y4UVK7V7IXHND3PJ4RUGGYRM7XYSUMYH|0    |['de']  |https://api.europeana.eu/record/199/item_Y4UVK7V7IXHND3PJ4RUGGYRM7XYSUMYH.json?wskey=ckwoetann|0                  |['German Digital Library']|['http://rightsstatements.org/vocab/InC/1.0/']|29.144974|1643634553187|2019-04-16T13:14:41.153Z|1555420481153          |2022-01-31T11:04:15.728Z|1643627055728         |['Feld mit Pflug und Egge']                          |IMAGE|[False]|
|6           |['Germany']|['Deutsches Dokumentationszentrum für Kunstgeschichte - Bildarchiv Foto Marburg']|['https://d-nb.info/gnd/118540416', 'http://data.europeana.eu/agent/base/59832']|{'def': ['https://d-nb.info/gnd/118540416', 'http://data.europeana.eu/agent/base/59832']}|{'de': ['Spaziergänger in einem öffentlichen Park im Regen']}|['199_DDB_BildarchivFotoMarburg']|['http://www.bildindex.de/bilder/d/nl00022f04']|['https://api.europeana.eu/thumbnail/v2/url.json?uri=http%3A%2F%2Fwww.bildindex.de%2Fbilder%2Fd%2Fnl00022f04&type=IMAGE']|nan             |nan                      |['199_DDB_BildarchivFotoMarburg']|6                    |https://www.europeana.eu/item/199/item_YUUHZCH66EOZT4SQX7U6DRAXNJLAK663?utm_source=api&utm_medium=api&utm_campaign=ckwoetann|/199/item_YUUHZCH66EOZT4SQX7U6DRAXNJLAK663|0    |['de']  |https://api.europeana.eu/record/199/item_YUUHZCH66EOZT4SQX7U6DRAXNJLAK663.json?wskey=ckwoetann|0                  |['German Digital Library']|['http://rightsstatements.org/vocab/InC/1.0/']|29.144974|1643645198416|2019-04-16T14:54:34.237Z|1555426474237          |2022-01-31T11:04:15.728Z|1643627055728         |['Spaziergänger in einem öffentlichen Park im Regen']|IMAGE|[False]|
|5           |['Germany']|['Deutsches Dokumentationszentrum für Kunstgeschichte - Bildarchiv Foto Marburg']|['https://d-nb.info/gnd/118540416', 'http://data.europeana.eu/agent/base/59832']|{'def': ['https://d-nb.info/gnd/118540416', 'http://data.europeana.eu/agent/base/59832']}|{'de': ['Am Tisch sitzender Bauer']}                         |['199_DDB_BildarchivFotoMarburg']|['http://www.bildindex.de/bilder/d/nl00068e14']|['https://api.europeana.eu/thumbnail/v2/url.json?uri=http%3A%2F%2Fwww.bildindex.de%2Fbilder%2Fd%2Fnl00068e14&type=IMAGE']|nan             |nan                      |['199_DDB_BildarchivFotoMarburg']|5                    |https://www.europeana.eu/item/199/item_2GLVYHXSMT6PAS7NCZ7ZLXWFDPAIG6CH?utm_source=api&utm_medium=api&utm_campaign=ckwoetann|/199/item_2GLVYHXSMT6PAS7NCZ7ZLXWFDPAIG6CH|0    |['de']  |https://api.europeana.eu/record/199/item_2GLVYHXSMT6PAS7NCZ7ZLXWFDPAIG6CH.json?wskey=ckwoetann|0                  |['German Digital Library']|['http://rightsstatements.org/vocab/InC/1.0/']|29.144974|1643628917287|2019-04-16T11:20:07.990Z|1555413607990          |2022-01-31T11:04:15.728Z|1643627055728         |['Am Tisch sitzender Bauer']                         |IMAGE|[False]|
|5           |['Germany']|['Deutsches Dokumentationszentrum für Kunstgeschichte - Bildarchiv Foto Marburg']|['https://d-nb.info/gnd/118540416', 'http://data.europeana.eu/agent/base/59832']|{'def': ['https://d-nb.info/gnd/118540416', 'http://data.europeana.eu/agent/base/59832']}|{'de': ['Drei Häuser in Saintes-Maries']}                    |['199_DDB_BildarchivFotoMarburg']|['http://www.bildindex.de/bilder/d/nl00022g04']|['https://api.europeana.eu/thumbnail/v2/url.json?uri=http%3A%2F%2Fwww.bildindex.de%2Fbilder%2Fd%2Fnl00022g04&type=IMAGE']|nan             |nan                      |['199_DDB_BildarchivFotoMarburg']|5                    |https://www.europeana.eu/item/199/item_2JULNTY6HMR6JLHNJHHOPCHEPW3UVHBO?utm_source=api&utm_medium=api&utm_campaign=ckwoetann|/199/item_2JULNTY6HMR6JLHNJHHOPCHEPW3UVHBO|0    |['de']  |https://api.europeana.eu/record/199/item_2JULNTY6HMR6JLHNJHHOPCHEPW3UVHBO.json?wskey=ckwoetann|0                  |['German Digital Library']|['http://rightsstatements.org/vocab/InC/1.0/']|29.144974|1643643659301|2019-04-16T13:01:49.906Z|1555419709906          |2022-01-31T11:04:15.728Z|1643627055728         |['Drei Häuser in Saintes-Maries']                    |IMAGE|[False]|
|5           |['Germany']|['Deutsches Dokumentationszentrum für Kunstgeschichte - Bildarchiv Foto Marburg']|['https://d-nb.info/gnd/118540416', 'http://data.europeana.eu/agent/base/59832']|{'def': ['https://d-nb.info/gnd/118540416', 'http://data.europeana.eu/agent/base/59832']}|{'de': ['Japonaiserie: Oiran']}                              |['199_DDB_BildarchivFotoMarburg']|['http://www.bildindex.de/bilder/d/fmc661302'] |['https://api.europeana.eu/thumbnail/v2/url.json?uri=http%3A%2F%2Fwww.bildindex.de%2Fbilder%2Fd%2Ffmc661302&type=IMAGE'] |nan             |nan                      |['199_DDB_BildarchivFotoMarburg']|5                    |https://www.europeana.eu/item/199/item_2JXHMPR4JFKCIZBSSEFBTIZDSQXFKRJ4?utm_source=api&utm_medium=api&utm_campaign=ckwoetann|/199/item_2JXHMPR4JFKCIZBSSEFBTIZDSQXFKRJ4|0    |['de']  |https://api.europeana.eu/record/199/item_2JXHMPR4JFKCIZBSSEFBTIZDSQXFKRJ4.json?wskey=ckwoetann|0                  |['German Digital Library']|['http://rightsstatements.org/vocab/InC/1.0/']|29.144974|1643646174589|2019-04-16T12:16:00.686Z|1555416960686          |2022-01-31T11:04:15.728Z|1643627055728         |['Japonaiserie: Oiran']                              |IMAGE|[False]|
|5           |['Germany']|['Deutsches Dokumentationszentrum für Kunstgeschichte - Bildarchiv Foto Marburg']|['http://data.europeana.eu/agent/base/59832', 'https://d-nb.info/gnd/118540416']|{'def': ['http://data.europeana.eu/agent/base/59832', 'https://d-nb.info/gnd/118540416']}|{'de': ['Olivenbäume']}                                      |['199_DDB_BildarchivFotoMarburg']|['http://www.bildindex.de/bilder/d/fmc661306'] |['https://api.europeana.eu/thumbnail/v2/url.json?uri=http%3A%2F%2Fwww.bildindex.de%2Fbilder%2Fd%2Ffmc661306&type=IMAGE'] |nan             |nan                      |['199_DDB_BildarchivFotoMarburg']|5                    |https://www.europeana.eu/item/199/item_2XU3Z44KCVJJZC5P7IC5Y2U6F7JVC6DU?utm_source=api&utm_medium=api&utm_campaign=ckwoetann|/199/item_2XU3Z44KCVJJZC5P7IC5Y2U6F7JVC6DU|0    |['de']  |https://api.europeana.eu/record/199/item_2XU3Z44KCVJJZC5P7IC5Y2U6F7JVC6DU.json?wskey=ckwoetann|0                  |['German Digital Library']|['http://rightsstatements.org/vocab/InC/1.0/']|29.144974|1643644888300|2019-04-16T12:23:34.823Z|1555417414823          |2022-01-31T11:04:15.728Z|1643627055728         |['Olivenbäume']                                      |IMAGE|[False]|
|5           |['Germany']|['Deutsches Dokumentationszentrum für Kunstgeschichte - Bildarchiv Foto Marburg']|['http://data.europeana.eu/agent/base/59832', 'https://d-nb.info/gnd/118540416']|{'def': ['http://data.europeana.eu/agent/base/59832', 'https://d-nb.info/gnd/118540416']}|{'de': ['Olivenhain']}                                       |['199_DDB_BildarchivFotoMarburg']|['http://www.bildindex.de/bilder/d/fmc652207'] |['https://api.europeana.eu/thumbnail/v2/url.json?uri=http%3A%2F%2Fwww.bildindex.de%2Fbilder%2Fd%2Ffmc652207&type=IMAGE'] |nan             |nan                      |['199_DDB_BildarchivFotoMarburg']|5                    |https://www.europeana.eu/item/199/item_2ZUYGKUUIRUMW4UOOKQZ3GQBSZTZHZQC?utm_source=api&utm_medium=api&utm_campaign=ckwoetann|/199/item_2ZUYGKUUIRUMW4UOOKQZ3GQBSZTZHZQC|0    |['de']  |https://api.europeana.eu/record/199/item_2ZUYGKUUIRUMW4UOOKQZ3GQBSZTZHZQC.json?wskey=ckwoetann|0                  |['German Digital Library']|['http://rightsstatements.org/vocab/InC/1.0/']|29.144974|1643644327387|2019-04-16T10:53:59.830Z|1555412039830          |2022-01-31T11:04:15.728Z|1643627055728         |['Olivenhain']                                       |IMAGE|[False]|

## Data Processing
Data Processing includes cleaning the `assets` table and extracting only some useful information. Extracted information include the following columns:
* country
* edmPreview
* provider
* title
* rights

Jobs 04-05 are devoted to Data Processing. The produced output is stored in a table, called `cleaned_assets`.
The following table shows an example of the produced table:
|country|edmpreview                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |provider              |title                                                                                                                                                     |rights                                           |
|-------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------|
|Belgium|https://api.europeana.eu/thumbnail/v2/url.json?uri=https%3A%2F%2Flib.is%2FIE2399340%2Fstream%3Fquality%3DLOW&type=IMAGE                                                                                                                                                                                                                                                                                                                                                                                                                                                   |PHOTOCONSORTIUM       |Vincent van Gogh. Weg achter de pastorietuin te Nuenen', 'Vincent van Gogh. Road behind the parsonage garden in Nuenen                                    |http://creativecommons.org/publicdomain/mark/1.0/|
|Belgium|https://api.europeana.eu/thumbnail/v2/url.json?uri=https%3A%2F%2Flib.is%2FIE2399256%2Fstream%3Fquality%3DLOW&type=IMAGE                                                                                                                                                                                                                                                                                                                                                                                                                                                   |PHOTOCONSORTIUM       |Vincent van Gogh. Portrait of Marcelle Roulin', 'Vincent van Gogh. Portret van Marcelle Roulin                                                            |http://creativecommons.org/publicdomain/mark/1.0/|
|Israel |https://api.europeana.eu/thumbnail/v2/url.json?uri=https%3A%2F%2Fwww.imj.org.il%2Fsites%2Fdefault%2Ffiles%2Fcollections%2Fgogh%2C%2520van-harvest%2520in%2520provence%7EB66_1039.jpg&type=IMAGE                                                                                                                                                                                                                                                                                                                                                                           |PHOTOCONSORTIUM       |Harvest in Provence                                                                                                                                       |http://rightsstatements.org/vocab/InC-EDU/1.0/   |
|Sweden |https://api.europeana.eu/thumbnail/v2/url.json?uri=http%3A%2F%2Fnationalmuseumse.iiifhosting.com%2Fiiif%2F84872e519f7a0b1d31a7b7dd5627fc8516929fc929daf64c900993b6831b25c2%2Ffull%2Ffull%2F0%2Fdefault.jpg&type=IMAGE                                                                                                                                                                                                                                                                                                                                                     |Museu                 |Blommande akaciagrenar', 'Acacia in Flowers                                                                                                               |http://creativecommons.org/publicdomain/mark/1.0/|
|Belgium|https://api.europeana.eu/thumbnail/v2/url.json?uri=https%3A%2F%2Flib.is%2FIE2399263%2Fstream%3Fquality%3DLOW&type=IMAGE                                                                                                                                                                                                                                                                                                                                                                                                                                                   |PHOTOCONSORTIUM       |Vincent van Gogh. Self portrait as painter', 'Vincent van Gogh. Zelfportret als schilder                                                                  |http://creativecommons.org/publicdomain/mark/1.0/|
|Belgium|https://api.europeana.eu/thumbnail/v2/url.json?uri=https%3A%2F%2Flib.is%2FIE2399298%2Fstream%3Fquality%3DLOW&type=IMAGE                                                                                                                                                                                                                                                                                                                                                                                                                                                   |PHOTOCONSORTIUM       |Vincent van Gogh. Landscape with train in the background', 'Vincent van Gogh. Landschap met trein op de achtergrond                                       |http://creativecommons.org/publicdomain/mark/1.0/|
|Belgium|https://api.europeana.eu/thumbnail/v2/url.json?uri=https%3A%2F%2Flib.is%2FIE2399228%2Fstream%3Fquality%3DLOW&type=IMAGE                                                                                                                                                                                                                                                                                                                                                                                                                                                   |PHOTOCONSORTIUM       |Vincent van Gogh. Bridge at Arles (Pont de Langlois)', 'Vincent van Gogh. Brug te Arles (Pont de Langlois)                                                |http://creativecommons.org/publicdomain/mark/1.0/|
|Belgium|https://api.europeana.eu/thumbnail/v2/url.json?uri=https%3A%2F%2Flib.is%2FIE2399249%2Fstream%3Fquality%3DLOW&type=IMAGE                                                                                                                                                                                                                                                                                                                                                                                                                                                   |PHOTOCONSORTIUM       |Vincent van Gogh. Portret van Armand Roulin', 'Vincent van Gogh. Portrait of Armand Roulin                                                                |http://creativecommons.org/publicdomain/mark/1.0/|
|Israel |https://api.europeana.eu/thumbnail/v2/url.json?uri=https%3A%2F%2Fwww.imj.org.il%2Fsites%2Fdefault%2Ffiles%2Fcollections%2FGogh%2C%2520van-Entrance%2520to%2520Voyer%2520dArgenson%2520Park%2520at%2520Asnires%7EL-B06_021.jpg&type=IMAGE                                                                                                                                                                                                                                                                                                                                  |PHOTOCONSORTIUM       |Entrance to Voyer-d'Argenson Park at Asnières                                                                                                             |http://rightsstatements.org/vocab/InC-EDU/1.0/   |

## Data Publication
The `view.py` script contains an app on the Online Exhibition, showing the preview of all the artworks contained in the database. To run the app, simply run the following command:
```
streamlit run view.py
```
