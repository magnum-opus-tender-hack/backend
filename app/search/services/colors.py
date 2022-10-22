from typing import List, Dict


def group(data: List[Dict], search_fields_d: List[Dict]) -> List[Dict]:
    search_fields = []
    search_fields_dict = []
    for x in search_fields_d:
        dat = dict(x)
        search_fields.append(dat["value"].lower())
        search_fields_dict.append(dat)
    re = {}
    n = 0
    for el in data:
        for field in search_fields:
            if field in el["name"].lower():
                if field in re:
                    re[field].append((n, 0, el["name"].lower().index(field)))
                else:
                    re[field] = []
                    re[field].append(
                        [x["type"] for x in search_fields_dict if x["value"] == field][
                            0
                        ]
                    )
                    re[field].append((n, 0, el["name"].lower().index(field)))
            m = 1
            for char in el["characteristic"]:
                if field in str(char["value"]).lower():
                    if field in re:
                        re[field].append(
                            (n, m, str(char["value"]).lower().index(field))
                        )
                    else:
                        re[field] = []
                        re[field].append(
                            [
                                x["type"]
                                for x in search_fields_dict
                                if x["value"].lower() == field
                            ][0]
                        )
                        re[field].append(
                            (n, m, str(char["value"]).lower().index(field))
                        )

                m += 1
        n += 1
    data += [re]
    return data
