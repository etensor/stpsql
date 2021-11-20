import psycopg2
import streamlit as st
import pandas as pd
import subprocess
import os

## David Penilla - 69675
## Santiago Abadia - 70770
## Jean Pierre Vargas - 69549

st.set_page_config(page_title='CovidApp | Bases de Datos', page_icon='U+2211')

# Esta App ya no se conecta con postgres local sino con una BD hosteada
# por heroku en aws que por seguridad tiene las credenciales protegidas.


def init_connection():
    # return psycopg2.connect(**st.secrets["postgres"])
    return psycopg2.connect(**st.secrets["db_credentials"])


def exec_query(query, mod=True):
    conn = init_connection()
    with conn.cursor() as c:
        c.execute(query)
        conn.commit()
        if mod:
            res = c.fetchall()
        conn.close()
        return res if mod else None


st.title('Covid - Control Estudiantes')


menu = ['Registrar', 'Buscar', 'Eliminar', 'Query Tool', 'Info']
choice = st.sidebar.selectbox("Taller - BD : Menu", menu)


if st.sidebar.button('Generar backup'):
    os.putenv("PGPASSWORD", f"{st.secrets['db_credentials']['password']}")
    res = subprocess.Popen(["pg_dump","-f", './dbackup_covid.sql',
        f"--host={st.secrets['db_credentials']['host']}",
        f"--port={st.secrets['db_credentials']['port']}",
        f"--username={st.secrets['db_credentials']['user']}",
        f"--dbname={st.secrets['db_credentials']['dbname']}"])
    res.wait()

    with open('./dbackup_covid.sql','rb') as file:
            download = st.sidebar.download_button(label='Descargar back-up',data=file,file_name='dbackup_covid.sql')
                                                        
###
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

        if temperatura > 38:
            st.warning(f"Advertencia, {nombre} podría estar enfermo.")
        st.success('Estudiante registrado correctamente.')


elif choice == 'Eliminar':
    st.subheader('Eliminar estudiante del registro')
    param = st.radio('Eliminar por:', ['nombre', 'codigo'])
    arg = st.text_input(f"Ingrese el {param}")

    if st.button('Confirmar'):
        exec_query(f"delete from students where {param} = {arg}", False)
        st.success('eliminado correctamente')


elif choice == 'Buscar':
    st.subheader('Buscar estudiante')
    param = st.radio(
        'Buscar por:', ['nombre', 'codigo', 'temperatura', 'plan'])
    arg = st.text_input(f"Ingrese el {param}")

    if st.button('Confirmar'):
        res = exec_query(f"select * from students where {param} = {arg};")
        with st.expander('Resultados Búsqueda', True):
            st.dataframe(pd.DataFrame(res))


elif choice == 'Query Tool':
    st.subheader("  PSQL ")
    req, res = st.columns(2)

    with req:
        with st.form(key='query'):
            query = st.text_area('consulte aqui')
            submit = st.form_submit_button(' Ejecutar ')

    with res:
        if submit:
            if (query.find('insert') and query.find('delete') != -1):
                exec_query(query, False)
            else:
                resultados = exec_query(query)
                st.success('Query procesada.')
                with st.expander('PSQL : Resultados'):
                    st.dataframe(pd.DataFrame(resultados))


if choice == 'Info':
    st.markdown(r'## Acerca: ')
    st.code(r'''
    
def init_connection():
    # return psycopg2.connect(**st.secrets["postgres"])
    return psycopg2.connect(**st.secrets["db_credentials"])

''','python')

    st.markdown('Nos conectamos a la base de datos con las credenciales')

    st.code(r'''

def exec_query(query, mod=True):
    conn = init_connection()
    with conn.cursor() as c:
        c.execute(query)
        conn.commit()
        if mod:
            res = c.fetchall()
        conn.close()
        return res if mod else None
 ''',"python")
    
    st.markdown('Si la query no retorna nada ``fetchall()`` falla.')
    
    st.subheader('**Trigger - postgres**')
    st.markdown('''
    Localmente, la base de datos necesita siguiente
    el trigger,implementado: ''')
    st.code(r'''-- Trigger -> Temperatura

        -- el trigger deberia ser con max(temperatura)
        -- pero si temprano max marca 41°; 40°,39°,38° 
        -- pasarian por una temperatura normal,
        -- lo cual determinaría con más certeza menos casos
        -- pero ignoraría a la mayoria.

    -- ---------------------------------------------------- 
        create or replace function verificar_estudiante()
    returns  trigger 
    language PLPGSQL as 
    $$
    declare
        ntemp double precision;
        nplan character varying;
    BEGIN
        ntemp := new.temperatura;
        
        -- requerido: 
        -- if (ntemp > (select max(temperatura) from students;) then

        if (ntemp > 38) then
            nplan := 'precaucion';		
        ELSE nplan := 'normal';
        end if;
        
        new.plan := nplan;
        return new;
    END;
    $$

    --

    create trigger trigverif
    before insert or update on students
    for each row execute procedure verificar_estudiante();
         
     ''','sql')

    st.subheader('Autores: ')
    st.markdown('David Penilla - 69675')
    st.markdown('Santiago Abadia - 70770')
    st.markdown('Jean Pierre Vargas - 69549')



sanos , control = st.columns(2)
tabla_est_sanos = exec_query('select * from estudiantes_sanos')
tabla_est_ctrl = exec_query('select * from estudiantes_control')

with sanos:
    with st.expander('Estudiantes Sanos: ', True):
        query_df = pd.DataFrame(tabla_est_sanos, 
        columns={'codigo', 'nombre', 'temp.'})

        st.dataframe(query_df)
    
with control:
    with st.expander('Estudiantes - Control: ', True):
        query_df = pd.DataFrame(tabla_est_ctrl, 
        columns={'codigo', 'nombre', 'temp.'})

        st.dataframe(query_df)


