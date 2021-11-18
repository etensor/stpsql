--
-- PostgreSQL database dump
--

-- Dumped from database version 13.4 (Ubuntu 13.4-4.pgdg20.04+1)
-- Dumped by pg_dump version 13.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: verificar_estudiante(); Type: FUNCTION; Schema: public; Owner: qgnrjgqbuhxuwe
--

CREATE FUNCTION public.verificar_estudiante() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
declare
	ntemp double precision;
	nplan character varying;
BEGIN
	ntemp := new.temperatura;
	if (ntemp > 37.8) then
		nplan := 'precaucion';		
	ELSE nplan := 'normal';
	end if;
	
	new.plan := nplan;
	return new;
END;
$$;


ALTER FUNCTION public.verificar_estudiante() OWNER TO qgnrjgqbuhxuwe;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: students; Type: TABLE; Schema: public; Owner: qgnrjgqbuhxuwe
--

CREATE TABLE public.students (
    codigo numeric NOT NULL,
    nombre character varying NOT NULL,
    plan character varying,
    temperatura double precision NOT NULL
);


ALTER TABLE public.students OWNER TO qgnrjgqbuhxuwe;

--
-- Name: estudiantes_control; Type: VIEW; Schema: public; Owner: qgnrjgqbuhxuwe
--

CREATE VIEW public.estudiantes_control AS
 SELECT students.codigo,
    students.nombre,
    students.temperatura
   FROM public.students
  WHERE ((students.plan)::text = 'precaucion'::text);


ALTER TABLE public.estudiantes_control OWNER TO qgnrjgqbuhxuwe;

--
-- Name: estudiantes_sanos; Type: VIEW; Schema: public; Owner: qgnrjgqbuhxuwe
--

CREATE VIEW public.estudiantes_sanos AS
 SELECT students.codigo,
    students.nombre,
    students.temperatura
   FROM public.students
  WHERE ((students.plan)::text = 'normal'::text);


ALTER TABLE public.estudiantes_sanos OWNER TO qgnrjgqbuhxuwe;

--
-- Data for Name: students; Type: TABLE DATA; Schema: public; Owner: qgnrjgqbuhxuwe
--

COPY public.students (codigo, nombre, plan, temperatura) FROM stdin;
420	estudiante	precaucion	38.2
1253	peperson	precaucion	38.9
8765	yepeto	normal	37.3
0	Alfa 	normal	37.5
\.


--
-- Name: students students_pkey; Type: CONSTRAINT; Schema: public; Owner: qgnrjgqbuhxuwe
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_pkey PRIMARY KEY (codigo);


--
-- Name: students trigverif; Type: TRIGGER; Schema: public; Owner: qgnrjgqbuhxuwe
--

CREATE TRIGGER trigverif BEFORE INSERT OR UPDATE ON public.students FOR EACH ROW EXECUTE FUNCTION public.verificar_estudiante();


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: qgnrjgqbuhxuwe
--

REVOKE ALL ON SCHEMA public FROM postgres;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO qgnrjgqbuhxuwe;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- Name: LANGUAGE plpgsql; Type: ACL; Schema: -; Owner: postgres
--

GRANT ALL ON LANGUAGE plpgsql TO qgnrjgqbuhxuwe;


--
-- PostgreSQL database dump complete
--

