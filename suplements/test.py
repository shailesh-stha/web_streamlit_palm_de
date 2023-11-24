import pandas as pd

def load_bundle(locale):
    df = pd.read_csv(r"./i18n/text_bundle.csv")
    df = df.query(f"locale == '{locale}'")

    lang_dict = {df.key.to_list()[i]: df.value.to_list()[i] for i in range(len(df.key.to_list()))}
    return lang_dict

lang = input("Please select EN or DE: ")
lang_dict = load_bundle(lang)

print(lang_dict['greeting'])
print(lang_dict['bye'])