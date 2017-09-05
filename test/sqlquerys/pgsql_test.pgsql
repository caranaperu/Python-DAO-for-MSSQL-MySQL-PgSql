select * from tb_maintable;

select directspInsertTest('XXX');


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