# **Covid Psql**

### App Taller BD

Para que correr app localmente:
crear carpeta './.streamlit'
adentro un archivo secrets.toml
con la configuracion local de postgres asi:

    [db_credentials]
    host = 
    port = 
    dbname =
    user = 
    password =

#### Para la configuración de psycopg2 por medio de st.secrets

Luego:
```bash
pip install -r requirements.txt

streamlit run stcovid_app.py

```

**  El boton ``Generar backup`` solo sirve localmente...**
