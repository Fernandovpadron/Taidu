--
-- PostgreSQL database dump
--

\restrict OMhfC7Af7MAkYR8mLxUyngdHgFLvBTC6QbvXIoz6s6RYgwsiid0aKqJ38ypI4BT

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: profiles_t; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.profiles_t (
    id integer NOT NULL,
    nombre character varying(50) NOT NULL,
    descripcion character varying(200)
);


ALTER TABLE public.profiles_t OWNER TO postgres;

--
-- Name: profiles_t_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.profiles_t_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.profiles_t_id_seq OWNER TO postgres;

--
-- Name: profiles_t_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.profiles_t_id_seq OWNED BY public.profiles_t.id;


--
-- Name: users_t; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users_t (
    id integer NOT NULL,
    username character varying(100) NOT NULL,
    email character varying(150) NOT NULL,
    profile_id integer NOT NULL,
    password_hash text
);


ALTER TABLE public.users_t OWNER TO postgres;

--
-- Name: users_t_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_t_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_t_id_seq OWNER TO postgres;

--
-- Name: users_t_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_t_id_seq OWNED BY public.users_t.id;


--
-- Name: profiles_t id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.profiles_t ALTER COLUMN id SET DEFAULT nextval('public.profiles_t_id_seq'::regclass);


--
-- Name: users_t id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users_t ALTER COLUMN id SET DEFAULT nextval('public.users_t_id_seq'::regclass);


--
-- Name: profiles_t profiles_t_nombre_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.profiles_t
    ADD CONSTRAINT profiles_t_nombre_key UNIQUE (nombre);


--
-- Name: profiles_t profiles_t_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.profiles_t
    ADD CONSTRAINT profiles_t_pkey PRIMARY KEY (id);


--
-- Name: users_t users_t_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users_t
    ADD CONSTRAINT users_t_email_key UNIQUE (email);


--
-- Name: users_t users_t_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users_t
    ADD CONSTRAINT users_t_pkey PRIMARY KEY (id);


--
-- Name: users_t users_t_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users_t
    ADD CONSTRAINT users_t_username_key UNIQUE (username);


--
-- Name: users_t fk_users_profile; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users_t
    ADD CONSTRAINT fk_users_profile FOREIGN KEY (profile_id) REFERENCES public.profiles_t(id);


--
-- PostgreSQL database dump complete
--

\unrestrict OMhfC7Af7MAkYR8mLxUyngdHgFLvBTC6QbvXIoz6s6RYgwsiid0aKqJ38ypI4BT

