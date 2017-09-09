CREATE TABLE [dbo].[tb_maintable](
	[pk_id] [int] IDENTITY(1,1) NOT NULL,
	[anytext] [nvarchar](10) NOT NULL,
 CONSTRAINT [PK_tb_maintable] PRIMARY KEY CLUSTERED
(
	[pk_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY];


CREATE TRIGGER [dbo].[tr_insertTest] ON  [dbo].[tb_maintable]
AFTER INSERT
AS
BEGIN
	IF (select anytext from inserted) <> 'DUMMY'
		insert into tb_maintable (anytext) values('DUMMY')
END;


create PROCEDURE [dbo].[directspInsertTest]
	@anytext nvarchar(10)
	AS
   	insert into tb_maintable(anytext) values (@anytext);
;
CREATE PROCEDURE [dbo].[withSelectspInsertTest]
	@anytext nvarchar(10)
	AS
	DECLARE @id int;
	--SET NOCOUNT OFF
	insert into tb_maintable (anytext) values(@anytext);

	set @id = SCOPE_IDENTITY();

	-- DEBE ESTAR PRIMERO !!!!!
    select @id
    select  * from tb_maintable;

;
CREATE PROCEDURE [dbo].[withReturnspInsertTest]
	@anytext nchar(10)
	AS
	DECLARE @id int;
    insert into tb_maintable (anytext) values(@anytext);
	set @id = SCOPE_IDENTITY();

    select  * from tb_maintable;
	return  @id;



CREATE PROCEDURE [dbo].[withOutParamInsertTest]
	@anytext nchar(10),
	@id int OUTPUT,
    @other_op varchar(10) OUTPUT
	AS

	insert into tb_maintable (anytext) values(@anytext);

	set @id = SCOPE_IDENTITY();
    set @other_op = 'SOY UN OUT PARAM';

    SELECT 'foo' AS thing UNION ALL SELECT 'bar' AS thing;
    SELECT 'xxx' AS thing UNION ALL SELECT 'byyyar' AS thing;

-- ---------------------------------------------------------------------------------------
-- ---------------------------------------------------------------------------------------
-- ---------------------------------------------------------------------------------------
-- ---------------------------------------------------------------------------------------
select * from tb_maintable;