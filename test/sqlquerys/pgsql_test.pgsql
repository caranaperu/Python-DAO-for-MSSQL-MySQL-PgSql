select * from tb_maintable;
;

select directspInsertTest('XXX');
select withSelectspInsertTest('YYY');
select withOutParamInsertTest('CCC');
select * from withOutParamInsertTest('DDDD') int key,other;

-- DROP TABLE tb_maintable;

CREATE TABLE tb_maintable
(
  id_key serial NOT NULL,
  anytext character varying(10) NOT NULL,
  CONSTRAINT pk_id PRIMARY KEY (id_key)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE tb_maintable
  OWNER TO postgres;



-- ALTER TABLE tb_maintable DROP CONSTRAINT pk_id;

ALTER TABLE tb_maintable
  ADD CONSTRAINT pk_id PRIMARY KEY(id_key);

-- TRIGGER
CREATE FUNCTION tr_insertTest() RETURNS trigger AS $$
    BEGIN
        IF NEW.anytext <> 'DUMMY' THEN
            	 insert into tb_maintable (anytext) values ('DUMMY');
        END IF;
        RETURN NULL;
    END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tbtr_insertTest  AFTER INSERT ON tb_maintable
FOR EACH ROW
EXECUTE PROCEDURE tr_insertTest();


-- Function: "directspInsertTest"(character varying)

-- DROP FUNCTION directspInsertTest(character varying);

CREATE OR REPLACE FUNCTION directspInsertTest(p_anytext character varying)
RETURNS INT AS
  $BODY$
  BEGIN
	insert into tb_maintable(id_key,anytext) values(DEFAULT,p_anytext) ;
	return 1;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE COST 100;





-- DROP FUNCTION withSelectspInsertTest(character varying);

CREATE OR REPLACE FUNCTION withSelectspInsertTest(p_anytext character varying)
RETURNS TABLE(lastid int) AS
  $BODY$
  DECLARE lastid INT;
  BEGIN
	insert into tb_maintable(id_key,anytext) values(DEFAULT,p_anytext) returning id_key into lastid;
	return query
		select lastid;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE COST 100;


CREATE OR REPLACE FUNCTION withReturnspInsertTest(p_anytext character varying)
RETURNS int AS
  $BODY$
  DECLARE lastid INT;
  BEGIN
	insert into tb_maintable(id_key,anytext) values(DEFAULT,p_anytext) returning id_key into lastid;
	return lastid;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE COST 100;


-- DROP FUNCTION withOutParamInsertTest(character varying,out int);

CREATE OR REPLACE FUNCTION withOutParamInsertTest(p_anytext character varying,out p_id int,out p_other int)
AS
  $BODY$
  BEGIN
  	p_other := 1000;
	  insert into tb_maintable(id_key,anytext) values(DEFAULT,p_anytext) returning id_key into p_id;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE COST 100;