Хорошо, давайте проанализируем JSON и определим, какие поля нужно использовать для извлечения даты и полного текстового описания патента.

**Анализ JSON:**

```json
{
    "common": {
        "document_number": "2550867",
        "application": {
            "number": "2014103924/11",
            "filing_date": "2014.02.04"
        },
        "kind": "C1",
        "publication_date": "2015.05.20",
        "guid": "d9a4f1a6-bd50-4205-9ca8-9829a38f964b",
        "citated_docs": [
            {
                "document_number": "92844",
                "kind": "U1",
                "identity": "RU92844U1",
                "publication_date": "2010.04.10",
                "id": "RU92844U1_20100410",
                "publishing_office": "RU",
                "found": true
            },
            {
                "document_number": "26704",
                "kind": "U1",
                "identity": "RU26704U1",
                "publication_date": "2002.12.10",
                "id": "RU26704U1_20021210",
                "publishing_office": "RU",
                "found": true
            },
           {
                "document_number": "20284",
                "kind": "U1",
                "identity": "RU20284U1",
                "publication_date": "2001.10.27",
                "id": "RU20284U1_20011027",
                "publishing_office": "RU",
                "found": true
            },
            {
                "document_number": "64144",
                "kind": "U1",
                "identity": "RU64144U1",
                "publication_date": "2007.06.27",
                "id": "RU64144U1_20070627",
                "publishing_office": "RU",
                "found": true
            },
            {
                "document_number": "2376158",
                "kind": "C2",
                "identity": "RU2376158C2",
                "publication_date": "2009.12.20",
                "id": "RU2376158C2_20091220",
                "publishing_office": "RU",
                "found": true
            }
        ],
        "classification": {
            "cpc": [
                {
                    "main_group": "10",
                    "classification_value": "A",
                    "subgroup": "7072",
                    "subclass": "T",
                    "section": "Y",
                    "fullname": "Y02T10/7072",
                    "class": "02"
                },
                {
                    "main_group": "10",
                    "classification_value": "A",
                    "subgroup": "72",
                    "subclass": "T",
                    "section": "Y",
                    "fullname": "Y02T10/72",
                    "class": "02"
                }
            ],
            "ipc": [
                {
                    "main_group": "55",
                    "classification_value": "I",
                    "subgroup": "00",
                    "subclass": "D",
                    "section": "B",
                    "fullname": "B62D55/00",
                    "class": "62"
                },
                {
                    "main_group": "50",
                    "classification_value": "I",
                    "subgroup": "10",
                    "subclass": "L",
                    "section": "B",
                    "fullname": "B60L50/10",
                    "class": "60"
                }
            ]
        },
        "publishing_office": "RU"
    },
    "meta": {
        "source": {
            "path": "0002550867",
            "from": "st96"
        }
    },
    "biblio": {
        "ru": {
            "citations": "RU 92844 U1, 10.04.2010. RU 26704 U1, 10.12.2002. RU 20284 U1, 27.10.2001. RU 64144 U1, 27.06.2007. RU 2376158 С2, 20.12.2009. CN 103269927 A, 28.08.2013",
            "inventor": [
                {
                    "name": "Коровин Владимир Андреевич (RU)"
                },
                {
                    "name": "Коровин Константин Владимирович (RU)"
                }
            ],
            "title": "ПРОМЫШЛЕННЫЙ ТРАКТОРНЫЙ АГРЕГАТ С ЭЛЕКТРОМЕХАНИЧЕСКОЙ ТРАНСМИССИЕЙ",
            "contact_data": "454119, г.Челябинск, ул. Машиностроителей, 10-Б, Коровину В.А.",
            "patentee": [
                {
                    "name": "Общество с ограниченной ответственностью \"Научно-производственное предприятие \"Резонанс\" (RU)"
                }
            ],
              "citations_parsed": [
                {
                    "doc": {
                        "document_number": "92844",
                        "kind": "U1",
                        "identity": "RU92844U1",
                        "publication_date": "2010.04.10",
                        "id": "RU92844U1_20100410",
                        "publishing_office": "RU",
                        "found": true
                    },
                    "text": "RU 92844 U1, 10.04.2010."
                },
                {
                    "doc": {
                        "document_number": "26704",
                        "kind": "U1",
                        "identity": "RU26704U1",
                        "publication_date": "2002.12.10",
                        "id": "RU26704U1_20021210",
                        "publishing_office": "RU",
                        "found": true
                    },
                    "text": "RU 26704 U1, 10.12.2002."
                },
                {
                     "doc": {
                        "document_number": "20284",
                        "kind": "U1",
                        "identity": "RU20284U1",
                        "publication_date": "2001.10.27",
                         "id": "RU20284U1_20011027",
                        "publishing_office": "RU",
                        "found": true
                     },
                     "text": "RU 20284 U1, 27.10.2001."
                },
                {
                    "doc": {
                        "document_number": "64144",
                        "kind": "U1",
                        "identity": "RU64144U1",
                        "publication_date": "2007.06.27",
                        "id": "RU64144U1_20070627",
                        "publishing_office": "RU",
                        "found": true
                    },
                    "text": "RU 64144 U1, 27.06.2007."
                },
                {
                    "doc": {
                        "document_number": "2376158",
                        "kind": "C2",
                        "identity": "RU2376158C2",
                        "publication_date": "2009.12.20",
                        "id": "RU2376158C2_20091220",
                        "publishing_office": "RU",
                         "found": true
                     },
                    "text": "RU 2376158 С2, 20.12.2009."
                },
                {
                    "text": "CN 103269927 A, 28.08.2013"
                }
            ]
        },
        "en": {
            "inventor": [
                {
                    "name": "Korovin Vladimir Andreevich (RU)"
                },
                {
                    "name": "Korovin Konstantin Vladimirovich (RU)"
                }
            ],
            "title": "INDUSTRIAL TRACTOR WITH ELECTROMECHANICAL TRANSMISSION",
            "contact_data": "454119, g.Cheljabinsk, ul. Mashinostroitelej, 10-B, Korovinu V.A.",
            "patentee": [
                {
                    "name": "Obshchestvo s ogranichennoj otvetstvennost'ju \"Nauchno-proizvodstvennoe predprijatie \"Rezonans\" (RU)"
                }
            ]
        }
    },
    "abstract": {
        "ru": "<pat:Abstract xmlns:pat=\"http://www.wipo.int/standards/XMLSchema/ST96/Patent\" xmlns:com=\"http://www.wipo.int/standards/XMLSchema/ST96/Common\" xmlns:mat=\"http://www.w3.org/1998/Math/MathML3\" xmlns:tbl=\"http://www.oasis-open.org/tables/exchange/1.0\" com:languageCode=\"ru\" pat:dataFormat=\"docdba\" pat:source=\"NATIONAL\"><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" style=\"display:block\"><p style=\"display: inline\">Изобретение относится к промышленным тракторам. Промышленный тракторный агрегат с электромеханической трансмиссией содержит двигатель, гусеничную ходовую часть, силовой генератор, связанный с двигателем, тяговый электродвигатель, связанный с гусеницами противоположных бортов, кабину с органами управления, рабочее оборудование и систему электрооборудования, соединенную с органами управления, с тяговым электродвигателем и приводами рабочего оборудования. Силовой генератор формирует многофазное переменное напряжение с частотой не менее 100 Гц. Система электрооборудования содержит выпрямитель выходного напряжения силового генератора. Привод рабочего оборудования или вала отбора мощности выполнен электрогидростатическим или электромеханическим с возможностью подключения цепей его силового электрического питания к силовому генератору или к выпрямителю. Повышается надежность работы тракторного агрегата. 21 з.п. ф-лы, 2 ил.</p></div></pat:Abstract>",
        "en": "<pat:Abstract xmlns:pat=\"http://www.wipo.int/standards/XMLSchema/ST96/Patent\" xmlns:com=\"http://www.wipo.int/standards/XMLSchema/ST96/Common\" xmlns:mat=\"http://www.w3.org/1998/Math/MathML3\" xmlns:tbl=\"http://www.oasis-open.org/tables/exchange/1.0\" com:languageCode=\"en\" pat:dataFormat=\"docdba\" pat:source=\"NATIONAL\"><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" style=\"display:block\"><p style=\"display: inline\">FIELD: transport.SUBSTANCE: this tractor comprises engine, caterpillar running gear, power generator coupled with the engine, traction motor coupled with caterpillars of opposite boards, cabin with control components, working equipment and electrical equipment system connected with control components, traction motor and working equipment drives. Power generator generates multiphase AV of 100 Hz frequency. Electric system comprises power generator output voltage rectifier. Hydro electrostatic or electromechanical drive of working equipment or power takeoff shaft is allows connection of its electric power supply circuits to power generator or rectifier.EFFECT: higher reliability.22 cl, 2 dwg</p></div></pat:Abstract>"
    },
      "claims": {
        "ru": "<pat:Claims xmlns:pat=\"http://www.wipo.int/standards/XMLSchema/ST96/Patent\" xmlns:com=\"http://www.wipo.int/standards/XMLSchema/ST96/Common\" xmlns:mat=\"http://www.w3.org/1998/Math/MathML3\" xmlns:tbl=\"http://www.oasis-open.org/tables/exchange/1.0\" com:languageCode=\"ru\" pat:dataFormat=\"original\" pat:source=\"NATIONAL\"><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" com:pNumber=\"1\"><p>1. Промышленный тракторный агрегат с электромеханической трансмиссией, содержащий двигатель внутреннего сгорания, гусеничную ходовую часть с ведущими и натяжными колесами, силовой генератор, связанный с двигателем, по меньшей мере, один тяговый электродвигатель, кинематически связанный с гусеницами противоположных бортов через бортовые редукторы, кабину с органами управления, рабочее оборудование с приводами его поступательного и/или вращательного перемещения, а также систему электрооборудования, соединенную с органами управления и, по меньшей мере, с одним тяговым электродвигателем и приводами рабочего оборудования, отличающийся тем, что силовой генератор приспособлен для формирования многофазного переменного напряжения с частотой не менее 100 Гц, система электрооборудования содержит выпрямитель выходного напряжения силового генератора, причем, по меньшей мере, один привод рабочего оборудования или вала отбора мощности выполнен электрогидростатическим или электромеханическим с возможностью подключения цепей его силового электрического питания к силовому генератору или к выпрямителю.</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" com:pNumber=\"2\"><p>2. Агрегат по п.1, отличающийся тем, что он содержит приводы рабочего оборудования, по меньшей мере, двух видов, различающихся способом передачи движения.</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" com:pNumber=\"3\"><p>3. Агрегат по п.2, отличающийся тем, что он содержит, по меньшей мере, один электромеханический, гидравлический, гидромеханический, электрогидравлический или электрогидростатический привод рабочего оборудования.</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" com:pNumber=\"4\"><p>4. Агрегат по любому из пп. 1, 2 или 3, отличающийся тем, что электрогидростатический привод имеет автономный гидравлический контур и содержит электродвигатель, соединенный с реверсивным нерегулируемым гидронасосом, выходные магистрали которого соединены с силовым гидроцилиндром или поворотным гидродвигателем, и гидравлический аккумулятор или гидравлический компенсатор, приспособленный для выполнения функции автономного гидробака.</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" com:pNumber=\"5\"><p>5. Агрегат по п.4, отличающийся тем, что электродвигатель электрогидростатического привода выполнен вентильно-индукторным с независимым возбуждением, или синхронным, или асинхронным, приспособленным для присоединения к выходным цепям силового генератора переменного тока непосредственно или через коммутационное устройство, причем система электрооборудования и входящее в ее состав коммутационное устройство выполнены с возможностью включения/выключения и/или изменения направления вращения этого электродвигателя в зависимости от сигналов, по меньшей мере, одного органа управления.</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" com:pNumber=\"6\"><p>6. Агрегат по п.4, отличающийся тем, что электродвигатель электрогидростатического привода выполнен вентильно-индукторным с самовозбуждением, или синхронным, или асинхронным, приспособленным для подключения к выходной цепи выпрямителя через преобразователь частоты или электронный контроллер, причем система электрооборудования и входящий в ее состав преобразователь частоты или электронный контроллер выполнены с возможностью изменения направления и/или скорости вращения этого электродвигателя в зависимости от сигналов, по меньшей мере, одного органа управления.</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" com:pNumber=\"7\"><p>7. Агрегат по п.4, отличающийся тем, что электродвигатель, гидронасос и гидроаккумулятор электрогидростатического привода встроены в гидроцилиндр или поворотный гидродвигатель этого привода или прикреплены к нему.</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" com:pNumber=\"8\"><p>8. Агрегат по п.1, отличающийся тем, что силовой генератор выполнен вентильно-индукторным с независимым возбуждением или синхронным, причем, по меньшей мере, один тяговый электродвигатель выполнен вентильно-индукторным с независимым возбуждением, или с самовозбуждением, или синхронным.</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" com:pNumber=\"9\"><p>9. Агрегат по любому из пп. 1, 5, 6, 7 или 8, отличающийся тем, что система электрооборудования выполнена с возможностью переключения числа пар полюсов силового генератора и/или электродвигателя привода и приспособлена для дискретного изменения скорости вращения этого электродвигателя.</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" com:pNumber=\"10\"><p>10. Агрегат по п.1, отличающийся тем, что он содержит электрогидростатические приводы механизмов натяжения гусениц.</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" com:pNumber=\"11\"><p>11. Агрегат по п.1 или 10, отличающийся тем, что система электрооборудования выполнена с возможностью измерения давления в гидроцилиндре или поворотном гидродвигателе электрогидростатического привода и/или скоростей вращения тяговых электродвигателей, а также приспособлена для управления этим электрогидростатическим приводом в зависимости от величин этого давления и/или скоростей вращения тяговых электродвигателей.</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" com:pNumber=\"12\"><p>12. Агрегат по п.10, отличающийся тем, что система электрооборудования приспособлена для управления электрогидростатическими приводами механизмов натяжения гусениц с возможностью поддержания предварительно установленной величины давления в гидроцилиндрах электрогидростатических приводов, и/или увеличения этого давления при повороте агрегата, и/или его снижения при неподвижном агрегате.</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" com:pNumber=\"13\"><p>13. Агрегат по п.1, отличающийся тем, что система электрооборудования состоит из высоковольтной части, содержащей, по меньшей мере, выпрямитель выходного напряжения силового генератора, коммутируемый тормозной резистор, а также, по меньшей мере, одно коммутационное устройство, и/или силовой преобразователь частоты, и/или электронный контроллер, приспособленные для управления, по меньшей мере, одним тяговым электродвигателем и/или электродвигателем привода рабочего оборудования, и низковольтной части, содержащей, по меньшей мере, один микропроцессорный контроллер, панель оператора, датчики параметров работы агрегата, устройства освещения, световой и звуковой сигнализации и систему электроснабжения низковольтной части, причем высоковольтная часть системы электрооборудования имеет гальваническую развязку от ее низковольтной части.</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" com:pNumber=\"14\"><p>14. Агрегат по п.13, отличающийся тем, что система электроснабжения содержит аккумулятор, а также низковольтный генератор или преобразователь напряжения, приспособленный для заряда этого аккумулятора, соответственно, от двигателя или от выходного напряжения силового генератора или выпрямителя.</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" com:pNumber=\"15\"><p>15. Агрегат по п.13, отличающийся тем, что панель оператора содержит цветную графическую панель, устройство звуковой или речевой сигнализации и органы управления этой панелью и/или агрегатом, выполненные в виде кнопок или клавиш.</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" com:pNumber=\"16\"><p>16. Агрегат по п.1 или 14, отличающийся тем, что он дополнительно содержит, по меньшей мере, одну автономную систему смазки бортовых редукторов и/или, по меньшей мере, одного механизма ходовой части и/или рабочего оборудования, содержащую электрический масляный насос, выполненный с возможностью подключения цепей его электропитания к выходным цепям силового генератора, или выпрямителя, или аккумулятора.</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" com:pNumber=\"17\"><p>17. Агрегат по п.1, отличающийся тем, что электрогидростатический или электромеханический привод имеет дополнительный орган управления, размещенный на этом приводе и приспособленный для управления его электродвигателем.</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" com:pNumber=\"18\"><p>18. Агрегат по п.1, отличающийся тем, что электрогидростатический или электромеханический привод оснащен датчиком перемещения и/или углового положения его выходного звена, а система электрооборудования приспособлена для управления его электродвигателем с возможностью стабилизации положения этого выходного звена или его приведения в положение, заданное органом управления.</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" com:pNumber=\"19\"><p>19. Агрегат по п.18, отличающийся тем, что датчик углового положения выходного звена электрогидростатического или электромеханического привода выполнен в виде микромеханического акселерометра, а система электрооборудования приспособлена для управления его электродвигателем с возможностью автоматической стабилизации положения этого выходного звена относительно гравитационной вертикали или его приведения в положение относительно гравитационной вертикали, заданное органом управления.</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" com:pNumber=\"20\"><p>20. Агрегат по любому из пп. 1, 10 или 14, отличающийся тем, что, по меньшей мере, один электромеханический или электрогидростатический привод рабочего оборудования или электрогидростатический привод механизма натяжения гусениц выполнен с возможностью подключения цепей его электропитания к аккумулятору низковольтной части системы электрооборудования.</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" com:pNumber=\"21\"><p>21. Агрегат по п.1 или 13, отличающийся тем, что, по меньшей мере, два устройства его системы электрооборудования объединенны между собой шиной последовательного интерфейса Controller Area Network (CAN) и/или Local Interconnect Network (LIN).</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" com:pNumber=\"22\"><p>22. Агрегат по п.1 или 13, отличающийся тем, что органы управления агрегатом выполнены в виде джойстиков управления движением и рабочим оборудованием, ключа запуска двигателя, рукоятки управления подачей топлива, педалей тормоза и деселератора.</p></div></pat:Claims>",
        "en": null
    },
  "description": {
        "ru": "<pat:Description xmlns:pat=\"http://www.wipo.int/standards/XMLSchema/ST96/Patent\" xmlns:com=\"http://www.wipo.int/standards/XMLSchema/ST96/Common\" xmlns:mat=\"http://www.w3.org/1998/Math/MathML3\" xmlns:tbl=\"http://www.oasis-open.org/tables/exchange/1.0\" com:languageCode=\"ru\" pat:dataFormat=\"original\" pat:source=\"NATIONAL\"><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" style=\"display:block\"><span style=\"font-weight: bold; padding-right: 20px\">[1]</span><p style=\"display: inline\" com:pNumber=\"1\">Изобретение относится к землеройным и строительно-дорожным машинам на базе промышленных тракторов, в том числе к бульдозерам, рыхлителям, кусторезам, корчевателям, траншеезасыпателям, ямобурам, трубоукладчикам, траншейным экскаваторам и т.п.</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" style=\"display:block\"><span style=\"font-weight: bold; padding-right: 20px\">[2]</span><p style=\"display: inline\" com:pNumber=\"2\">Известен гусеничный трактор с электромеханической трансмиссией, содержащий тепловой двигатель, связанный с силовым генератором, два тяговых электродвигателя, кинематически связанных с гусеницами противоположных бортов, и систему управления, в состав которой входят преобразователь напряжения и микропроцессорный контроллер [1].</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" style=\"display:block\"><span style=\"font-weight: bold; padding-right: 20px\">[3]</span><p style=\"display: inline\" com:pNumber=\"3\">Его недостатком являются ограниченные функциональные возможности. Это обусловлено отсутствием реализации в его системе управления функций управления рабочим оборудованием, агрегатируемым с этим трактором.</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" style=\"display:block\"><span style=\"font-weight: bold; padding-right: 20px\">[4]</span><p style=\"display: inline\" com:pNumber=\"4\">Наиболее близким к предложенному является бульдозерно-рыхлительный агрегат на базе дизель-электрического трактора ДЭТ-250М2 с электромеханической трансмиссией, содержащие кинематически соединенный с двигателем внутреннего сгорания электрический генератор постоянного тока, подключенный к нему тяговый электродвигатель, выходной вал которого связан с осевым валом, соединенным с входными валами левого и правого механизмов поворота планетарного типа, выходные валы которых, в свою очередь, через бортовые редукторы связаны с ведущими звездочками гусеничной ходовой части трактора, а также систему электрооборудования трактора, гидравлическую систему приводов перемещения бульдозерного и рыхлительного оборудования и кабину с системами жизнеобеспечения и органами управления [2].</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" style=\"display:block\"><span style=\"font-weight: bold; padding-right: 20px\">[5]</span><p style=\"display: inline\" com:pNumber=\"5\">Недостатком этого тракторного агрегата является его пониженная надежность, что обусловлено применением гидравлических приводов рабочего оборудования, имеющих, по сравнению с электромеханическими приводами, более низкую надежность ввиду наличия рабочей жидкости и необходимости прокладки гидравлических магистралей к гидроцилиндрам, расположенным на подвижных рабочих органах. Нарушение герметичности любого гидравлического компонента, вследствие применения объединенной гидросистемы управления рабочим оборудованием с общим гидробаком, приводит к потере рабочей жидкости во всей гидравлической системе и к нарушению работоспособности всех приводов. К пониженной надежности этого тракторного агрегата приводит также применение коллекторных электромашин и отсутствие систем централизованной смазки и автоматического натяжения гусениц ходовой части трактора.</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" style=\"display:block\"><span style=\"font-weight: bold; padding-right: 20px\">[6]</span><p style=\"display: inline\" com:pNumber=\"6\">Техническим результатом, на достижение которого направлено изобретение во всех вариантах его реализации, является повышение надежности работы промышленного тракторного агрегата с электромеханической трансмиссий.</p></div><div xmlns:ns4=\"http://www.oasis-open.org/tables/exchange/1.0\" xmlns:ns3=\"http://www.w3.org/1998/Math/MathML3\" style=\"display:block\"><span style=\"font-weight: bold; padding-right: 20px\">[7]</span><p style=\"display: inline\" com:pNumber