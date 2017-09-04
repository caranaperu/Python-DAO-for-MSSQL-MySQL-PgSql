select * from tb_factura4
select * from tb_factura

execute uspaddFactura4 2499,'2499';
execute uspaddFactura5 2407,'2407';
set nocount on;declare @id int; EXEC @id = uspaddFactura5 2409,'2409';select @id as return_value

set nocount on;declare @id int;EXEC uspaddFactura6 2410,'2410',@id output;select @id;

create PROCEDURE [dbo].[uspaddFactura3]
    @factura_id int,
	@name nchar(10)
	AS
   	insert into tb_factura4(factura_id,factura_fecha,name,tb_factura_item_id) values (@factura_id,GETDATE(),@name,2);
    --select  * from tb_factura4;
;

ALTER PROCEDURE [dbo].[uspaddFactura4]
    @factura_id int,
	@name nchar(10)
	AS
	DECLARE @id int;
	DECLARE @id2 int;
	--SET NOCOUNT OFF
   insert into tb_factura4(factura_id,factura_fecha,name,tb_factura_item_id) values (@factura_id,GETDATE(),@name,2);

	set @id = SCOPE_IDENTITY();

    set @factura_id = @factura_id+100
    set @name = replace(@name,' ','')  + 's'
    insert into tb_factura4(factura_id,factura_fecha,name,tb_factura_item_id) values (@factura_id,GETDATE(),@name,2);
    select  * from tb_factura4;
    select @id






ALTER TRIGGER [dbo].[tr_test] ON  [dbo].[tb_factura4]
AFTER INSERT
AS
BEGIN
   -- SET NOCOUNT ON added to prevent extra result sets from
    --insert into tb_factura(factura_fecha) values(getdate());
    insert into tb_factura (factura_fecha) values(GETDATE())
END




alter PROCEDURE [dbo].[uspaddFactura5]
    @factura_id int,
	@name nchar(10)
	AS
	DECLARE @id int;
    insert into tb_factura4(factura_id,factura_fecha,name,tb_factura_item_id) values (@factura_id,GETDATE(),@name,2);

	set @id = SCOPE_IDENTITY();

	set @factura_id = @factura_id+100
	set @name = replace(@name,' ','')  + 's'
	insert into tb_factura4(factura_id,factura_fecha,name,tb_factura_item_id) values (@factura_id,GETDATE(),@name,2);
    select  * from tb_factura4;

	return  @id;


ALTER PROCEDURE [dbo].[uspaddFactura6]
    @factura_id int,
	@name nchar(10),
	@id int OUTPUT,
    @pp varchar(10) OUTPUT
	AS

    insert into tb_factura4(factura_id,factura_fecha,name,tb_factura_item_id) values (@factura_id,GETDATE(),@name,2);

	set @id = SCOPE_IDENTITY();
    set @pp = 'SOY UN OUT PARAM';

	set @factura_id = @factura_id+100
	set @name = replace(@name,' ','')  + 's'
	insert into tb_factura4(factura_id,factura_fecha,name,tb_factura_item_id) values (@factura_id,GETDATE(),@name,2);
    SELECT 'foo' AS thing UNION ALL SELECT 'bar' AS thing;
    SELECT 'xxx' AS thing UNION ALL SELECT 'byyyar' AS thing;
