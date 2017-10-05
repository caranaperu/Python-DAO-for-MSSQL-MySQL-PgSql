--
-- PostgreSQL database dump
--

-- Dumped from database version 9.3.15
-- Dumped by pg_dump version 9.3.19
-- Started on 2017-09-30 00:23:44 PET

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

DROP DATABASE db_pytest;
--
-- TOC entry 2051 (class 1262 OID 286244)
-- Name: db_pytest; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE db_pytest WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'es_PE.UTF-8' LC_CTYPE = 'es_PE.UTF-8';


ALTER DATABASE db_pytest OWNER TO postgres;

\connect db_pytest

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 1 (class 3079 OID 11829)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner:
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 2054 (class 0 OID 0)
-- Dependencies: 1
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner:
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

--
-- TOC entry 189 (class 1255 OID 286263)
-- Name: directspinserttest(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION directspinserttest(p_anytext character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
  BEGIN
	insert into tb_maintable(id_key,anytext) values(DEFAULT,p_anytext) ;
	return 1;
  END;
  $$;


ALTER FUNCTION public.directspinserttest(p_anytext character varying) OWNER TO postgres;

--
-- TOC entry 190 (class 1255 OID 286268)
-- Name: tr_inserttest(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION tr_inserttest() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        IF NEW.anytext <> 'DUMMY' THEN
            	 insert into tb_maintable (anytext) values ('DUMMY');
        END IF;
        RETURN NULL;
    END;
$$;


ALTER FUNCTION public.tr_inserttest() OWNER TO postgres;

--
-- TOC entry 193 (class 1255 OID 286282)
-- Name: withoutparaminserttest(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION withoutparaminserttest(p_anytext character varying, OUT p_id integer, OUT p_other integer) RETURNS record
    LANGUAGE plpgsql
    AS $$
  BEGIN
  	p_other := 1000;
	insert into tb_maintable(id_key,anytext) values(DEFAULT,p_anytext) returning id_key into p_id;
  END;
  $$;


ALTER FUNCTION public.withoutparaminserttest(p_anytext character varying, OUT p_id integer, OUT p_other integer) OWNER TO postgres;

--
-- TOC entry 192 (class 1255 OID 286280)
-- Name: withreturnspinserttest(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION withreturnspinserttest(p_anytext character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
  DECLARE lastid INT;
  BEGIN
	insert into tb_maintable(id_key,anytext) values(DEFAULT,p_anytext) returning id_key into lastid;
	return lastid;
  END;
  $$;


ALTER FUNCTION public.withreturnspinserttest(p_anytext character varying) OWNER TO postgres;

--
-- TOC entry 191 (class 1255 OID 286279)
-- Name: withselectspinserttest(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION withselectspinserttest(p_anytext character varying) RETURNS TABLE(lastid integer)
    LANGUAGE plpgsql
    AS $$
  DECLARE lastid INT;
  BEGIN
	insert into tb_maintable(id_key,anytext) values(DEFAULT,p_anytext) returning id_key into lastid;
	return query
		select lastid;
  END;
  $$;


ALTER FUNCTION public.withselectspinserttest(p_anytext character varying) OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 172 (class 1259 OID 286247)
-- Name: tb_maintable; Type: TABLE; Schema: public; Owner: postgres; Tablespace:
--

CREATE TABLE tb_maintable (
    id_key integer NOT NULL,
    anytext character varying(10) NOT NULL
);


ALTER TABLE public.tb_maintable OWNER TO postgres;

--
-- TOC entry 176 (class 1259 OID 286360)
-- Name: tb_maintable_ckeys; Type: TABLE; Schema: public; Owner: postgres; Tablespace:
--

CREATE TABLE tb_maintable_ckeys (
    main_code character varying(5) NOT NULL,
    main_number integer NOT NULL,
    anytext character varying(10) NOT NULL
);


ALTER TABLE public.tb_maintable_ckeys OWNER TO postgres;

--
-- TOC entry 174 (class 1259 OID 286342)
-- Name: tb_maintable_fk; Type: TABLE; Schema: public; Owner: postgres; Tablespace:
--

CREATE TABLE tb_maintable_fk (
    pk_id integer NOT NULL,
    anytext character varying(10) NOT NULL,
    fktest integer NOT NULL,
    nondup character varying(100)
);


ALTER TABLE public.tb_maintable_fk OWNER TO postgres;

--
-- TOC entry 173 (class 1259 OID 286340)
-- Name: tb_maintable_fk_pk_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE tb_maintable_fk_pk_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tb_maintable_fk_pk_id_seq OWNER TO postgres;

--
-- TOC entry 2055 (class 0 OID 0)
-- Dependencies: 173
-- Name: tb_maintable_fk_pk_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE tb_maintable_fk_pk_id_seq OWNED BY tb_maintable_fk.pk_id;


--
-- TOC entry 171 (class 1259 OID 286245)
-- Name: tb_maintable_id_key_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE tb_maintable_id_key_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tb_maintable_id_key_seq OWNER TO postgres;

--
-- TOC entry 2056 (class 0 OID 0)
-- Dependencies: 171
-- Name: tb_maintable_id_key_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE tb_maintable_id_key_seq OWNED BY tb_maintable.id_key;


--
-- TOC entry 175 (class 1259 OID 286349)
-- Name: tb_testfk; Type: TABLE; Schema: public; Owner: postgres; Tablespace:
--

CREATE TABLE tb_testfk (
    fktest integer NOT NULL
);


ALTER TABLE public.tb_testfk OWNER TO postgres;

--
-- TOC entry 1920 (class 2604 OID 286250)
-- Name: id_key; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY tb_maintable ALTER COLUMN id_key SET DEFAULT nextval('tb_maintable_id_key_seq'::regclass);


--
-- TOC entry 1921 (class 2604 OID 286345)
-- Name: pk_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY tb_maintable_fk ALTER COLUMN pk_id SET DEFAULT nextval('tb_maintable_fk_pk_id_seq'::regclass);


--
-- TOC entry 2042 (class 0 OID 286247)
-- Dependencies: 172
-- Data for Name: tb_maintable; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY tb_maintable (id_key, anytext) FROM stdin;
1	2297
2	2297
3	2297
4	2297
5	2297
175	2297
7	2297
8	2297
176	DUMMY
177	2297
178	DUMMY
179	XXX
180	DUMMY
14	test3
15	test3
16	XXX
181	YYY
18	2297
19	2297
20	XXX
21	2297
22	2297
23	2297
182	DUMMY
183	CCC
26	XXX
27	2297
28	DUMMY
184	DUMMY
185	2297
186	DUMMY
187	2297
188	DUMMY
189	XXX
35	YYY
36	DUMMY
37	2297
38	DUMMY
39	2297
40	DUMMY
41	CCC
42	DUMMY
43	2297
44	DUMMY
45	CCC
46	DUMMY
47	2297
48	DUMMY
49	2297
50	DUMMY
51	2297
52	DUMMY
53	XXX
54	DUMMY
55	YYY
56	DUMMY
57	CCC
58	DUMMY
59	XXX
60	DUMMY
61	YYY
62	DUMMY
63	CCC
64	DUMMY
65	2297
66	DUMMY
67	XXX
68	DUMMY
69	YYY
70	DUMMY
71	CCC
72	DUMMY
73	XXX
74	DUMMY
75	YYY
76	DUMMY
77	CCC
78	DUMMY
79	2297
80	DUMMY
81	2297
82	DUMMY
83	XXX
84	DUMMY
85	YYY
86	DUMMY
87	CCC
88	DUMMY
89	XXX
90	DUMMY
91	YYY
92	DUMMY
93	CCC
94	DUMMY
95	2297
96	DUMMY
97	2297
98	DUMMY
99	2297
100	DUMMY
101	2297
102	DUMMY
103	2297
104	DUMMY
105	XXX
106	DUMMY
107	YYY
108	DUMMY
109	CCC
110	DUMMY
111	XXX
112	DUMMY
113	YYY
114	DUMMY
115	CCC
116	DUMMY
117	2297
118	DUMMY
119	2297
120	DUMMY
121	2297
122	DUMMY
123	2297
124	DUMMY
125	XXX
126	DUMMY
127	YYY
128	DUMMY
129	CCC
130	DUMMY
131	XXX
132	DUMMY
133	YYY
134	DUMMY
135	CCC
136	DUMMY
137	2297
138	DUMMY
139	XXX
140	DUMMY
141	YYY
142	DUMMY
143	CCC
144	DUMMY
145	2297
146	DUMMY
147	XXX
148	DUMMY
149	YYY
150	DUMMY
151	CCC
152	DUMMY
153	2297
154	DUMMY
155	2297
156	DUMMY
157	2297
158	DUMMY
159	2297
160	DUMMY
161	2297
162	DUMMY
163	XXX
164	DUMMY
165	YYY
166	DUMMY
167	CCC
168	DUMMY
169	XXX
170	DUMMY
171	YYY
172	DUMMY
173	CCC
174	DUMMY
190	DUMMY
191	YYY
192	DUMMY
193	CCC
194	DUMMY
195	XXX
196	DUMMY
197	YYY
198	DUMMY
199	CCC
200	DUMMY
201	XXX
202	DUMMY
203	YYY
204	DUMMY
205	CCC
206	DUMMY
207	XXX
208	DUMMY
209	YYY
210	DUMMY
211	CCC
212	DUMMY
213	2297
214	DUMMY
217	2297
218	DUMMY
219	2297
220	DUMMY
221	2297
222	DUMMY
229	test
230	DUMMY
231	test
232	DUMMY
233	test
234	DUMMY
237	test
238	DUMMY
239	test
240	DUMMY
241	test
242	DUMMY
243	test
244	DUMMY
245	test
246	DUMMY
247	test
248	DUMMY
249	test
250	DUMMY
251	test
252	DUMMY
253	test
254	DUMMY
255	test
256	DUMMY
257	test
258	DUMMY
259	test
260	DUMMY
\.


--
-- TOC entry 2046 (class 0 OID 286360)
-- Dependencies: 176
-- Data for Name: tb_maintable_ckeys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY tb_maintable_ckeys (main_code, main_number, anytext) FROM stdin;
008	8	Soy 0007
009	9	Soy 0009
\.


--
-- TOC entry 2044 (class 0 OID 286342)
-- Dependencies: 174
-- Data for Name: tb_maintable_fk; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY tb_maintable_fk (pk_id, anytext, fktest, nondup) FROM stdin;
2	test	1	U4W24TG6HW
3	test	1	RESXIUGR0D
4	test	1	RYRKO40NVD
8	test	1	WGPGCNE8NG
9	test	1	IsDuplicate22
10	test	1	El segundo 22
15	test	1	IsDuplicate24
16	test	1	El segundo 24
\.


--
-- TOC entry 2057 (class 0 OID 0)
-- Dependencies: 173
-- Name: tb_maintable_fk_pk_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('tb_maintable_fk_pk_id_seq', 16, true);


--
-- TOC entry 2058 (class 0 OID 0)
-- Dependencies: 171
-- Name: tb_maintable_id_key_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('tb_maintable_id_key_seq', 260, true);


--
-- TOC entry 2045 (class 0 OID 286349)
-- Dependencies: 175
-- Data for Name: tb_testfk; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY tb_testfk (fktest) FROM stdin;
1
\.


--
-- TOC entry 1923 (class 2606 OID 286252)
-- Name: pk_id; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY tb_maintable
    ADD CONSTRAINT pk_id PRIMARY KEY (id_key);


--
-- TOC entry 1927 (class 2606 OID 286347)
-- Name: pk_tb_maintable_fk; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY tb_maintable_fk
    ADD CONSTRAINT pk_tb_maintable_fk PRIMARY KEY (pk_id);


--
-- TOC entry 1929 (class 2606 OID 286353)
-- Name: pk_testfk; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY tb_testfk
    ADD CONSTRAINT pk_testfk PRIMARY KEY (fktest);


--
-- TOC entry 1931 (class 2606 OID 286364)
-- Name: unq_key_test; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY tb_maintable_ckeys
    ADD CONSTRAINT unq_key_test UNIQUE (main_code, main_number);


--
-- TOC entry 1924 (class 1259 OID 286359)
-- Name: fki_testfk; Type: INDEX; Schema: public; Owner: postgres; Tablespace:
--

CREATE INDEX fki_testfk ON tb_maintable_fk USING btree (fktest);


--
-- TOC entry 1925 (class 1259 OID 286348)
-- Name: ix_nondup; Type: INDEX; Schema: public; Owner: postgres; Tablespace:
--

CREATE UNIQUE INDEX ix_nondup ON tb_maintable_fk USING btree (nondup);


--
-- TOC entry 1933 (class 2620 OID 286269)
-- Name: tbtr_inserttest; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tbtr_inserttest AFTER INSERT ON tb_maintable FOR EACH ROW EXECUTE PROCEDURE tr_inserttest();


--
-- TOC entry 1932 (class 2606 OID 286354)
-- Name: fk_testfk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY tb_maintable_fk
    ADD CONSTRAINT fk_testfk FOREIGN KEY (fktest) REFERENCES tb_testfk(fktest);


--
-- TOC entry 2053 (class 0 OID 0)
-- Dependencies: 7
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2017-09-30 00:23:44 PET

--
-- PostgreSQL database dump complete
--

