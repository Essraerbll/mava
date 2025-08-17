import pandas as pd

# Dosyayı oku
df = pd.read_csv('mardin.csv')

# visit_date sütununda slashtan sonrasını sil
df['visit_date'] = df['visit_date'].str.split('/').str[0]

# review_text sütununda slashtan sonrasını sil
df['review_text'] = df['review_text'].str.split('/').str[0]

# Eğer "devamını oku" gibi ifadeleri de silmek istiyorsan:
df['review_text'] = df['review_text'].str.replace('devamını oku', '', case=False)

# Temizlenmiş veriyi yeni bir dosyaya kaydet
df.to_csv('mardin_temiz.csv', index=False)