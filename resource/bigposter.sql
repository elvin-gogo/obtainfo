--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: obtainfo_bigposter; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE obtainfo_bigposter (
    id integer NOT NULL,
    link character varying(512) NOT NULL,
    image character varying(512) NOT NULL,
    title character varying(64) NOT NULL,
    "timestamp" timestamp with time zone NOT NULL
);


ALTER TABLE public.obtainfo_bigposter OWNER TO postgres;

--
-- Name: obtainfo_bigposter_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE obtainfo_bigposter_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.obtainfo_bigposter_id_seq OWNER TO postgres;

--
-- Name: obtainfo_bigposter_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE obtainfo_bigposter_id_seq OWNED BY obtainfo_bigposter.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY obtainfo_bigposter ALTER COLUMN id SET DEFAULT nextval('obtainfo_bigposter_id_seq'::regclass);


--
-- Data for Name: obtainfo_bigposter; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY obtainfo_bigposter (id, link, image, title, "timestamp") FROM stdin;
3	http://movie.obtainfo.com/detail/539c128a95f9e9737656b67c/	http://img02.taobaocdn.com/imgextra/i2/495498642/TB2B3iQaVXXXXcJXXXXXXXXXXXX_!!495498642.jpg	明日边缘	2014-10-29 11:35:14.193+08
4	http://movie.obtainfo.com/detail/5379ce9b3faf8617f19ca31f/	http://img02.taobaocdn.com/imgextra/i2/495498642/TB21uiPaVXXXXXxXpXXXXXXXXXX_!!495498642.jpg	天才眼睛狗	2014-10-29 11:35:43.467+08
5	http://movie.obtainfo.com/detail/539c112e95f9e9737656b67b/	http://img03.taobaocdn.com/imgextra/i3/495498642/TB2UW9TaVXXXXaMXXXXXXXXXXXX_!!495498642.jpg	X战警：逆转未来	2014-10-29 11:36:09.939+08
6	http://movie.obtainfo.com/detail/539c24b795f9e9737656b682/	http://img02.taobaocdn.com/imgextra/i2/495498642/TB2tdiTaVXXXXaSXXXXXXXXXXXX_!!495498642.jpg	哥斯拉2014	2014-10-29 11:36:32.185+08
7	http://movie.obtainfo.com/detail/5379ce9c3faf8617f19ca7a4/	http://img04.taobaocdn.com/imgextra/i4/495498642/TB20GOUaVXXXXalXXXXXXXXXXXX_!!495498642.jpg	驯龙高手2	2014-10-29 11:36:53.22+08
8	http://movie.obtainfo.com/detail/53fa929095f9e943eed2e39f/	http://img03.taobaocdn.com/imgextra/i3/495498642/TB2D21OaVXXXXadXpXXXXXXXXXX_!!495498642.jpg	四大名捕大结局	2014-10-29 11:37:10.719+08
\.


--
-- Name: obtainfo_bigposter_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('obtainfo_bigposter_id_seq', 8, true);


--
-- Name: obtainfo_bigposter_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY obtainfo_bigposter
    ADD CONSTRAINT obtainfo_bigposter_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

