USE [db_pytest]
GO
/****** Object:  StoredProcedure [dbo].[directspInsertTest]    Script Date: 27/09/2017 12:11:21 a.m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE PROCEDURE [dbo].[directspInsertTest]
	@anytext nvarchar(10)
	AS
   	insert into tb_maintable(anytext) values (@anytext);


GO
/****** Object:  StoredProcedure [dbo].[withOutParamInsertTest]    Script Date: 27/09/2017 12:11:21 a.m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
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
GO
/****** Object:  StoredProcedure [dbo].[withReturnspInsertTest]    Script Date: 27/09/2017 12:11:21 a.m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[withReturnspInsertTest]
	@anytext nchar(10)
	AS
	DECLARE @id int;
    insert into tb_maintable (anytext) values(@anytext);
	set @id = SCOPE_IDENTITY();

    select  * from tb_maintable;
	return  @id;
GO
/****** Object:  StoredProcedure [dbo].[withSelectspInsertTest]    Script Date: 27/09/2017 12:11:21 a.m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[withSelectspInsertTest]
	@anytext nvarchar(10)
	AS
	DECLARE @id int;
	DECLARE @id2 int;
	--SET NOCOUNT OFF
	insert into tb_maintable (anytext) values(@anytext);

	set @id = SCOPE_IDENTITY();

	-- DEBE ESTAR PRIMERO !!!!!
    select @id
    select  * from tb_maintable;

GO
/****** Object:  Table [dbo].[tb_maintable]    Script Date: 27/09/2017 12:11:21 a.m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[tb_maintable](
	[pk_id] [int] IDENTITY(1,1) NOT NULL,
	[anytext] [nvarchar](10) NOT NULL,
 CONSTRAINT [PK_tb_maintable] PRIMARY KEY CLUSTERED
(
	[pk_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
/****** Object:  Table [dbo].[tb_maintable_ckeys]    Script Date: 27/09/2017 12:11:21 a.m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[tb_maintable_ckeys](
	[main_code] [nvarchar](5) NOT NULL,
	[main_number] [int] NOT NULL,
	[anytext] [nvarchar](10) NOT NULL
) ON [PRIMARY]

GO
/****** Object:  Table [dbo].[tb_maintable_fk]    Script Date: 27/09/2017 12:11:21 a.m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[tb_maintable_fk](
	[pk_id] [int] IDENTITY(1,1) NOT NULL,
	[anytext] [nvarchar](10) NOT NULL,
	[fktest] [int] NOT NULL,
	[nondup] [nvarchar](100) NULL,
 CONSTRAINT [PK_tb_maintable_fk] PRIMARY KEY CLUSTERED
(
	[pk_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [IX_tb_maintable_fk] UNIQUE NONCLUSTERED
(
	[nondup] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
/****** Object:  Table [dbo].[tb_testfk]    Script Date: 27/09/2017 12:11:21 a.m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[tb_testfk](
	[fktest] [int] NOT NULL,
 CONSTRAINT [PK_tb_testfk] PRIMARY KEY CLUSTERED
(
	[fktest] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
ALTER TABLE [dbo].[tb_maintable_fk]  WITH CHECK ADD  CONSTRAINT [FK_tb_maintable_fk_tb_testfk] FOREIGN KEY([fktest])
REFERENCES [dbo].[tb_testfk] ([fktest])
GO
ALTER TABLE [dbo].[tb_maintable_fk] CHECK CONSTRAINT [FK_tb_maintable_fk_tb_testfk]
GO
