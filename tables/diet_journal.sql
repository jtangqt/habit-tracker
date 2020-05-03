--
-- PostgreSQL database dump
--

-- Dumped from database version 12.2
-- Dumped by pg_dump version 12.2

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
-- Name: diet_journal; Type: TABLE; Schema: public; Owner: jtangqt
--

CREATE TABLE public.diet_journal (
    date date NOT NULL,
    "Food Journal" jsonb,
    "Weight (kg)" numeric(4,2),
    "Measurements" jsonb,
    "Fasting Start Time" time with time zone,
    "Water (Cups)" integer,
    "Exercise" jsonb
);


ALTER TABLE public.diet_journal OWNER TO jtangqt;

--
-- Data for Name: diet_journal; Type: TABLE DATA; Schema: public; Owner: jtangqt
--

COPY public.diet_journal (date, "Food Journal", "Weight (kg)", "Measurements", "Fasting Start Time", "Water (Cups)", "Exercise") FROM stdin;
\.


--
-- Name: diet_journal diet_journal_pkey; Type: CONSTRAINT; Schema: public; Owner: jtangqt
--

ALTER TABLE ONLY public.diet_journal
    ADD CONSTRAINT diet_journal_pkey PRIMARY KEY (date);


--
-- Name: idx_date; Type: INDEX; Schema: public; Owner: jtangqt
--

CREATE INDEX idx_date ON public.diet_journal USING btree (date DESC);


--
-- PostgreSQL database dump complete
--

