--
-- PostgreSQL database dump
--

-- Dumped from database version 14.5 (Debian 14.5-1.pgdg110+1)
-- Dumped by pg_dump version 14.3

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: employee; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.employee (
    id integer NOT NULL,
    firstname character varying NOT NULL,
    "position" character varying NOT NULL,
    date_insert date NOT NULL,
    date_update date NOT NULL,
    lastname character varying NOT NULL,
    username character varying NOT NULL,
    password character varying NOT NULL,
    email character varying NOT NULL
);


ALTER TABLE public.employee OWNER TO admin;

--
-- Name: employee_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.employee ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.employee_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: images; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.images (
    id bigint NOT NULL,
    image_path character varying NOT NULL,
    date_insert timestamp without time zone NOT NULL,
    date_update timestamp without time zone NOT NULL,
    ticket_id bigint NOT NULL
);


ALTER TABLE public.images OWNER TO admin;

--
-- Name: images_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.images ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.images_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: ticket_types; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.ticket_types (
    id integer NOT NULL,
    type_name character varying NOT NULL,
    date_insert timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    date_update timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.ticket_types OWNER TO admin;

--
-- Name: ticket_types_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.ticket_types ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.ticket_types_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tickets; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.tickets (
    id bigint NOT NULL,
    user_id_created bigint NOT NULL,
    ticket_type_id integer NOT NULL,
    ticket_text character varying NOT NULL,
    telegram_chatid character varying NOT NULL,
    is_done boolean DEFAULT false NOT NULL,
    sended boolean DEFAULT false NOT NULL,
    text_response character varying,
    note character varying,
    employee_id integer,
    date_insert timestamp without time zone NOT NULL,
    date_update timestamp without time zone NOT NULL,
    telegram_message_id bigint,
    is_working boolean DEFAULT false
);


ALTER TABLE public.tickets OWNER TO admin;

--
-- Name: tickets_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.tickets ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tickets_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.users (
    id bigint NOT NULL,
    telegram_username character varying,
    telegram_fullname character varying,
    date_insert timestamp without time zone NOT NULL,
    date_update timestamp without time zone
);


ALTER TABLE public.users OWNER TO admin;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.users ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: voices; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.voices (
    id bigint NOT NULL,
    voice_path character varying NOT NULL,
    date_insert timestamp without time zone NOT NULL,
    date_update timestamp without time zone NOT NULL,
    ticket_id bigint NOT NULL
);


ALTER TABLE public.voices OWNER TO admin;

--
-- Name: voices_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.voices ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.voices_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: employee employee_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_pk PRIMARY KEY (id);


--
-- Name: users newtable_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT newtable_pk PRIMARY KEY (id);


--
-- Name: ticket_types ticket_types_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.ticket_types
    ADD CONSTRAINT ticket_types_pk PRIMARY KEY (id);


--
-- Name: tickets tickets_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_pk PRIMARY KEY (id);


--
-- Name: voices voice_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.voices
    ADD CONSTRAINT voice_pk PRIMARY KEY (id);


--
-- Name: images images_fk; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_fk FOREIGN KEY (ticket_id) REFERENCES public.tickets(id) ON DELETE CASCADE;


--
-- Name: tickets tickets_fk_ticket_types; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_fk_ticket_types FOREIGN KEY (ticket_type_id) REFERENCES public.ticket_types(id);


--
-- Name: tickets tickets_fk_users; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_fk_users FOREIGN KEY (user_id_created) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

