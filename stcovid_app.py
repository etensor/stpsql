import psycopg2
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title='CovidApp 9', page_icon='🦠')


# Esta App ya no se conecta con postgres local sino con un BD hosteada
# por heroku en aws que por seguridad tiene las credenciales protegidas.


#@st.experimental_singleton
def init_connection():
    #return psycopg2.connect(**st.secrets["postgres"])
    #return psycopg2.connect(os.environ.get('DATABASE_URL'))
    return psycopg2.connect(**st.secrets.db_credentials)


def exec_query(query, mod = True):
    conn = init_connection()
    with conn.cursor() as c:
        c.execute(query)
        conn.commit()
        if mod:
            res = c.fetchall()
        conn.close()
        return res if mod else None

st.title('Covid - Control Estudiantes')

tabla_est = exec_query('select * from students;')


menu = ['Registrar','Buscar','Eliminar','Query Tool','Info']
choice = st.sidebar.selectbox("Taller - BD : Menu",menu)
with st.sidebar.expander("BD - JSON"):
    st.write(tabla_est)

if choice == 'Registrar':
    st.subheader('Añadir estudiante al registro')
    datos = st.form(key='estudiante')
    nombre = datos.text_input('Nombre: ')
    codigo = datos.number_input('Código: ', min_value=0000, step=1)
    temperatura = datos.slider(
        'Temperatura: ', min_value=35.0, max_value=44.0, value=37.5, step=0.1)
    submit = datos.form_submit_button('Confirmar y añadir')
    if submit:
        exec_query('insert into public.students(codigo,nombre,temperatura) '
                + f'values ({codigo},\'{nombre}\', {temperatura});', False)

        st.success('Estudiante registrado correctamente.')

elif choice == 'Eliminar':
    st.subheader('Eliminar estudiante del registro')
    param = st.radio('Eliminar por:', ['nombre','codigo'])
    arg = st.text_input(f"Ingrese el {param}")

    if st.button('Confirmar'):
        exec_query(f"delete from students where {param} = {arg}", False)
        st.success('eliminado correctamente')


elif choice == 'Buscar':
    st.subheader('Buscar estudiante')
    param = st.radio('Buscar por:', ['nombre', 'codigo','temperatura','plan'])
    arg = st.text_input(f"Ingrese el {param}")

    if st.button('Confirmar'):
        res = exec_query(f"select * from students where {param} = {arg};")
        with st.expander('Resultados Búsqueda',True):
            st.dataframe(pd.DataFrame(res))




elif choice == 'Query Tool':
    st.subheader("  PSQL ")
    req,res = st.columns(2)

    with req:
        with st.form(key='query'):
            query = st.text_area('consulte aqui')
            submit = st.form_submit_button(' Ejecutar ')
    

    with res:
        if submit:
            if (query.find('insert') and query.find('delete')!= -1):
                exec_query(query,False)                
            else:
                resultados = exec_query(query)
                st.success('Query procesada.')
                with st.expander('PSQL : Resultados'):
                    st.dataframe(pd.DataFrame(resultados))


with st.expander(" Tabla: ",True):
    query_df = pd.DataFrame(tabla_est)
    st.dataframe(query_df)

