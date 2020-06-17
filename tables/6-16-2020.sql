--
-- PostgreSQL database dump
--

-- Dumped from database version 12.3
-- Dumped by pg_dump version 12.3

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
-- Name: todo_list; Type: TABLE; Schema: public; Owner: jtangqt
--

CREATE TABLE public.todo_list (
    idx integer NOT NULL,
    task_name character varying(100) NOT NULL,
    created_on timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    schedule jsonb,
    is_complete jsonb,
    next_occurrence timestamp with time zone,
    project jsonb,
    parent_task integer,
    task_dependencies jsonb,
    related_tasks jsonb,
    goal character varying(100),
    habit boolean
);


ALTER TABLE public.todo_list OWNER TO jtangqt;

--
-- Name: todo_list_idx_seq; Type: SEQUENCE; Schema: public; Owner: jtangqt
--

CREATE SEQUENCE public.todo_list_idx_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.todo_list_idx_seq OWNER TO jtangqt;

--
-- Name: todo_list_idx_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jtangqt
--

ALTER SEQUENCE public.todo_list_idx_seq OWNED BY public.todo_list.idx;


--
-- Name: todo_list idx; Type: DEFAULT; Schema: public; Owner: jtangqt
--

ALTER TABLE ONLY public.todo_list ALTER COLUMN idx SET DEFAULT nextval('public.todo_list_idx_seq'::regclass);


--
-- Data for Name: diet_journal; Type: TABLE DATA; Schema: public; Owner: jtangqt
--

COPY public.diet_journal (date, "Food Journal", "Weight (kg)", "Measurements", "Fasting Start Time", "Water (Cups)", "Exercise") FROM stdin;
2020-06-12	{"Lunch": [], "Snack": [], "Dinner": [], "Breakfast": [{"name": "coffee", "calories": 8}, {"name": "bagel", "calories": 300}], "Midnight Snack": []}	55.90	{"Bust": null, "Hips": null, "Neck": null, "Waist": 27, "Left Arm": null, "Right Arm": null, "Left Thigh": null, "Right Thigh": null}	22:33:00-04	\N	{"minutes": 2, "accomplishments": "literally did nothing today"}
\.


--
-- Data for Name: todo_list; Type: TABLE DATA; Schema: public; Owner: jtangqt
--

COPY public.todo_list (idx, task_name, created_on, schedule, is_complete, next_occurrence, project, parent_task, task_dependencies, related_tasks, goal, habit) FROM stdin;
13	leetcode	2020-06-16 22:14:30.432287-04	\N	\N	\N	\N	\N	\N	\N	\N	\N
14	leetcode	2020-06-16 22:14:34.103068-04	\N	\N	\N	\N	\N	\N	\N	\N	\N
\.


--
-- Name: todo_list_idx_seq; Type: SEQUENCE SET; Schema: public; Owner: jtangqt
--

SELECT pg_catalog.setval('public.todo_list_idx_seq', 14, true);


--
-- Name: diet_journal diet_journal_pkey; Type: CONSTRAINT; Schema: public; Owner: jtangqt
--

ALTER TABLE ONLY public.diet_journal
    ADD CONSTRAINT diet_journal_pkey PRIMARY KEY (date);


--
-- Name: todo_list todo_list_pkey; Type: CONSTRAINT; Schema: public; Owner: jtangqt
--

ALTER TABLE ONLY public.todo_list
    ADD CONSTRAINT todo_list_pkey PRIMARY KEY (idx);


--
-- Name: idx_date; Type: INDEX; Schema: public; Owner: jtangqt
--

CREATE INDEX idx_date ON public.diet_journal USING btree (date DESC);


--
-- PostgreSQL database dump complete
--

