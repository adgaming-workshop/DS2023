#!/usr/bin/env python
# coding: utf-8

# In[2]:





# In[14]:





# In[21]:


import streamlit as st
from PIL import Image

Image1 = Image.open('Image1.jpg')
Image2 = Image.open('Image2.jpg')
Image0 = Image.open('all.jpg')
Image3 = Image.open('kfc.jpg')
Image4 = Image.open('мак.jpg')
Image5 = Image.open('Бурегер.jpg')
Image6 = Image.open('теремок.jpg')

codepiece1 = '''def yandex_maps_api(api_key, place, region):
    
    # Создаем пустой pandas.DataFrame в котором будем хранить данные
    # Колонки: Place - название кафе
    #          Adress - Адрес
    #          Region - Регион
    
    df = pd.DataFrame(columns = ['Place', 'Address', 'Region']) 
    url = 'https://search-maps.yandex.ru/v1/'
    search_request = f'{place} {region}'
    i=0
    
    while True:
        params = {'apikey': api_key, 'text': search_request, 'lang': 'ru_RU',
                 'results':50, 'skip':50*i}
        data = requests.get(url, params = params)
    
        info = data.json()
        
        if len(info['features'])==0:
            break
        
        temp_df = pd.DataFrame()
        place_col, city_col, reg_col = [], [], []
        for place in info['features']:
            place_col.append(place['properties']['name'])
            try:
                city_col.append(place['properties']['CompanyMetaData']['address'])
                reg_col.append(place['properties']['CompanyMetaData']['address'].split(',')[0])
            except KeyError:
                city_col.append('Закрыто')
                reg_col.append('Закрыто')
        
        temp_df['Place'] = place_col
        temp_df['Address'] = city_col
        temp_df['Region'] = reg_col
        #temp_df['Requested_region'] = [region]*len(temp_df)

        df = df.append(temp_df)
        i+=1
        if i==200: # ограничение Api
            break 
    
    return df'''
codepiece2 = '''def parse_region_names(browser): # Ввести браузер

    ref = 'https://www.gks.ru/bgd/regl/b04_42/IssWWW.exe/Stg/d010/i011830r.htm'
    browser.get(ref)
    element = browser.find_element(by=By.CSS_SELECTOR, value="table")
    text = element.text
    browser.quit()
    
    regions = re.findall(r'\d\. [^\n]+', text)
    
    new_regions = []

    for region in regions:
        if re.match(r'.*округ', region) == None and re.match(r'.*числе', region) == None :
            new_regions.append(region.split('. ')[-1].rstrip())
            
    return new_regions[1:]'''

codepiece4 = '''df.drop_duplicates(subset = 'Address', inplace = True)
df = df[df['Place'].isin(places)]
def parse_region_capitals():
    
    page = requests.get('https://ru.wikipedia.org/wiki/Субъекты_Российской_Федерации').text
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find('table', class_="standard sortable")

    df = pd.read_html(str(table))
    df = pd.concat(df)
    df = df[['Адм. центр/столица','Субъект Российской Федерации']]
    df = df.dropna()
    df['Субъект Российской Федерации'] = [re.findall(r'[^0-9\[\]]*', i)[0] for i in df['Субъект Российской Федерации']]
    
    d = {}
    for key, value in zip(df['Адм. центр/столица'], df['Субъект Российской Федерации']):
        d.update({key : value})
    return(d)
capital_dict = parse_region_capitals()
new_regions = []

for reg in df['Region']:
    try:
        new_regions.append(capital_dict[reg])
    except KeyError:
        new_regions.append(reg)'''
codepiece5 = '''def distribution_by_region(df, n):  # Функция для построения топ n регионов по кол-ву точек фастфуда
    
    data = df.groupby(by='Region', as_index=False).count()
    
    print(f'Топ {n} регионов по кол-ву точек фастфуда\n')
    
    if n > len(df['Region'].unique()):
        n = len(df['Region'].unique())
    
    for reg, count in zip(data.sort_values(by='Place', ascending=False)['Region'][:n], 
                          data.sort_values(by='Place', ascending=False)['Place'][:n]):
        print(f'{reg} - {count}')
        
    sns.barplot(data = df.groupby(by='Region', as_index=False).count()\    # построение графика
            .sort_values(by='Place', ascending=False)[:20], x = 'Region', y = 'Place')

plt.xticks(rotation=-90)
plt.ylabel('Number of places') '''
codepiece6 = '''sns.barplot(data = df.groupby(by='Place', as_index=False).count()            .sort_values(by='Region', ascending=False), x = 'Region', y = 'Place')

plt.xlabel('Number of places')
plt.xticks(rotation=-90)'''
codepiece7 = '''# см. в Final.html'''

st.markdown("# FAST FOOD STATS Project")

st.markdown("## Предисловие")
st.markdown('''В данном проекте проводится:
- Анализ количества точек сетей быстрого питания (Вкусно и точка, KFC, Burger King, Теремок) в разбивке по субъектам РФ;
- Вычисление доли каждой из 4 выбранных сетей относительно количества остальных в регионе, построение карты.
''')
st.markdown("P.S. Ячейки кода предоставлены для отражения логики. Для полноценного запуска и дополнительных деталей обратитесь к Final.html из репозитория")

st.markdown("## Часть 1. Получение данных")
st.markdown("Для проведения исследования понадобились данные о точках быстрого питания, а также список субъектов РФ. Пройдемся по порядку.")
st.markdown("###Яндекс.Карты")
st.markdown('''Из Яндекс.Карт парсятся данные о работающих точках по всей РФ. Парсинг происходит из поисковой выдачи Карт с помощью API Поиска по организациям от Yandex.
Инструкция по получению ключа для api:
- Перейти по ссылке https://yandex.ru/dev/maps/geosearch/?from=mapsapi
- Нажать "Получить ключ"
- Заполнить контактные данные (Цель: учебный проект)
- Скопировать ключ в переменную ниже
Функция ниже отправляет запрос на поиск мест в яндекс картах. Запрос состоит из названия места place и региона поиска region. На выходе функция выдает pandas.DataFrame с адресом и регионом найденных по запросу мест")
Стоит отметить, что API позволяет спарсить не более 1000 строк за один запрос, но, благо, количество открытых точек даже по всем 4 выбранным сетям вместе удовлетворяет это условие для каждого региона.''')
st.code(codepiece1, language='python')
st.markdown("###Субъекты РФ")
st.markdown("2. Информация о субъектах парсится Cелениумом с сайта Росстата ('https://www.gks.ru/bgd/regl/b04_42/IssWWW.exe/Stg/d010/i011830r.htm'). Полученные значения обработаем с помощью регулярных выражений. Нужно для итерирования по всем субъектам в предыдущем пункте.")
st.code(codepiece2, language='python')
st.markdown("Полученные данные укладываются в датафрейм Pandas, но об этом отдельно.")
    
st.markdown("## Часть 2. Работа с датафреймом")
    
st.markdown('''Уложенные в датафрейм данные нужно очистить. Проведено две стадии фильтрации:
- **Фильтр от точек вне региона**. Т.к. API не смотрит на принадлежность локации к региону, а проверяет лишь попадание в прямоугольник, внутрь которого вписываются все точки региона.
Таким образом, в датасет попадают и точки в "углах" прямоугольника, не принадлежащие региону.''')
st.markdown('''- **Дедубликация** (например, "Вкусно - и точка" и "Вкусно - и точка.Авто", находящиеся в одном здании, парсятся как две самостоятельные точки).''')
st.markdown('''Помимо этого, было обнаружено что если ресторан находился в столице региона, то его адрес был, например, не "Смоленская область, Смоленск...", а "Смоленск, ...".
Поэтому спарсим также столицы регионов и сделаем словарь из полученных пар, а затем поменяем столицы в поле Region на названия регионов. Также по запросу выдавались не только перечисленные места, но и похожие. Их тоже надо отбросить.
Итоговая предобработка:''')
st.code(codepiece4, language='python')

st.markdown("## Часть 3. Количество точек по регионам / количество точек по сетям")
st.markdown("После получения данных переходим к их визуализации. Для начала, построим barplot (Seaborn) c топ-20 регионов с максимальным количеством точек по всем 4 сетям:")
st.code(codepiece5, language='python')
st.image(Image1, caption='Топ-20 регионов по количеству ресторанов')
st.markdown("Здесь результаты вполне предсказуемы. Построим barplot с количеством точек в разбивке по франшизам:")
st.code(codepiece6, language='python')
st.image(Image2, caption='Количество ресторанов по сетям')
st.markdown('''Интересно! Видимо пока иностранные сети фаст-фуда уходят, "Теремок" расширяется''')
st.markdown("## Часть 4. Работа с картой, доля каждой сети по регионам")
st.markdown('''Наконец, покажем долю точек каждой из сетей относительно всех остальных в регионах. Покажем эти доли на картах с помощью Folium и Geopandas.
Построение карты РФ была взята из существующего проекта, с адаптацией под данный проект:''')
st.code(codepiece7, language='python')

st.markdown("Получились вот такие карты по долям каждой из сетей. Сначала покажем распределение общего количества ресторанов, а затем доли по регионам:")
st.image(Image0, caption='Количество ресторанов сетей (KFC, Вкусно и точка, Burger King), Теремок по регионам РФ. Темно-красный - max%')
st.image(Image3, caption='Доля ресторанов KFC в регионах РФ. Рыжий - max%')
st.image(Image4, caption='Доля ресторанов Вкусно и точка в регионах РФ. Темно-коричневый - max%')
st.image(Image5, caption='Доля ресторанов Burger King  в регионах РФ. Фиолетовый - max%')
st.image(Image6, caption='Доля ресторанов Теремок в регионах РФ. Голубой - max%')


st.markdown("На этом все!")
st.markdown("**Исходный код см. в Final.html**")


# In[10]:




