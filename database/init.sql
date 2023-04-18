CREATE TABLE IF NOT EXISTS public.socmed_aggs_socmedaggs (
    id bigint NOT NULL,
    social_media character varying(32) NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    count integer NOT NULL,
    unique_count integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
