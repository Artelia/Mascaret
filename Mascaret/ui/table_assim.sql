-- Table: test_assim3.assim_config

-- DROP TABLE IF EXISTS test_assim3.assim_config;

CREATE TABLE IF NOT EXISTS test_assim3.assim_config
(
    id_type integer NOT NULL DEFAULT nextval('test_assim3.assim_config_id_type_seq'::regclass),
    control_var text COLLATE pg_catalog."default" NOT NULL,
    perturbation_var text[] COLLATE pg_catalog."default",
    perturbation_val double precision[],
    seuil_rejet_misfit double precision,
    iterations_sigma integer,
    active boolean NOT NULL DEFAULT false,
    control_type text COLLATE pg_catalog."default",
    CONSTRAINT assim_config_pkey PRIMARY KEY (id_type)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS test_assim3.assim_config
    OWNER to postgres;

-- Table: test_assim3.assim_ks

-- DROP TABLE IF EXISTS test_assim3.assim_ks;

CREATE TABLE IF NOT EXISTS test_assim3.assim_ks
(
    id_zone integer NOT NULL,
    id_type integer NOT NULL,
    active_min boolean,
    std_min double precision,
    val_inf_min double precision,
    val_sup_min double precision,
    abs_min double precision,
    abs_max double precision,
    branchnum integer,
    lst_obs integer[],
    std_maj double precision,
    active_maj boolean,
    val_inf_maj double precision,
    val_sup_maj double precision,
    auto_del boolean
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS test_assim3.assim_ks
    OWNER to postgres;

-- Table: test_assim3.assim_law

-- DROP TABLE IF EXISTS test_assim3.assim_law;

CREATE TABLE IF NOT EXISTS test_assim3.assim_law
(
    id_law integer NOT NULL,
    id_type integer NOT NULL,
    val_min double precision,
    val_max double precision,
    lst_obs integer[],
    active_a boolean,
    std_a double precision,
    active_b boolean,
    std_b double precision,
    auto_del boolean,
    source_law text,
    CONSTRAINT assim_law_pkey PRIMARY KEY (id_law, id_type)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS test_assim3.assim_law
    OWNER to postgres;