setup_data = {
    "model":{
        "field1": {"type": "int"},
        "field2": {"type": "float"},
        "field3": {"type": "long"}
    },
    "columns": {
        "campo1": "field1",
        "campo2": "field2"
    },
    "order_fields": [
        {
            "field": "field1",
            "desc": "true"
        },
        {
            "field": "field2",
            "desc": "false"
        }
    ]
}
order_Fields_pos = ["field1","field2"]

print(setup_data["model"]["field1"])
print(setup_data["colmapping"]["campo1"])

print(order_Fields_pos.index("field2"))
order_Fields_pos.remove("field1")
print(order_Fields_pos.index("field2"))
print(order_Fields_pos.index(setup_data["colmapping"]["campo2"]))
print(setup_data["order_fields"][0])

