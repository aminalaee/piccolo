from typing import Any, List

from .alter import Alter
from .columns import Column
from .query import (
    Create,
    Delete,
    Drop,
    Exists,
    Insert,
    Raw,
    Select,
    TableExists,
    Update,
)
from .utils import _camel_to_snake


class Database(object):

    async def run(*queries):
        """
        Use asyncio.gather here ...
        """
        pass


class TableMeta(type):

    def __new__(cls, name, bases, namespace, **kwds):
        """
        Automatically populate the tablename, and columns.
        """
        table = super().__new__(cls, name, bases, namespace)

        Meta = namespace.get('Meta')
        tablename = getattr(Meta, 'tablename', None) if Meta else None
        if not tablename:
            table.Meta.tablename = _camel_to_snake(name)

        columns = []
        for key, value in namespace.items():
            if issubclass(type(value), Column):
                columns.append(value)
                value.name = key

        table.Meta.columns = columns
        return table


class Table(metaclass=TableMeta):

    class Meta:
        tablename = None
        columns: List[Column] = []

    def __init__(self, **kwargs):
        self.data = kwargs

    def __setitem__(self, key: str, value: Any):
        self.data[key] = value

    def __getitem__(self, key: str):
        return self.data[key]

    def __str__(self):
        """
        Need to return them in the correct order ...
        """
        # If there's no matching attribute on data, get the default from
        # the column
        # Put __setattr__ on the columns as well? Either raise exception
        # Or use it to proxy to data??? Would be pretty awesome ...
        pass

    @classmethod
    def select(cls, *column_names: str) -> Select:
        """
        Needs to be a simple wrapper.

        One thing I *might* want to do is have an AS string, or just allow
        that in the string. For example, 'foo as bar'. I think I'll make
        it more explicit. So you do As('foo', 'bar'). So we can easily
        inspect that the column exists, and what we're trying to map it
        to doesn't already exist.
        """
        if len(column_names) == 0:
            columns_str = '*'
        else:
            # TODO - make sure the columns passed in are valid
            columns_str = ', '.join(column_names)

        return Select(
            table=cls,
            base=f'SELECT {columns_str} from {cls.Meta.tablename}'
        )

    @classmethod
    def insert(cls) -> Insert:
        """
        In typing is it possible to distinguish between a class and a class
        instance?

        Pokemon.insert(
            Pokemon(name="jigglypuff", power=500, trainer="florence")
        )

        Need to allow things like:

        jigglypuff = Pokemon(name="jigglypuff", power=500, trainer="florence")

        Pokemon.insert(jigglypuff)

        jigglypuff.power = 600
        # this is where save would be useful ...
        # save could be an alias to self.__cls__.save(self)
        # it just depends if the instance has an id set yet
        # if no id, use self.__cls__.insert(self)
        # if an id, use self.__cls__.update(**self.columns)

        It depends how far wen want to go with ORM style
        -> need to avoid properties which trigger ORM queries
        --> dot lookups should just return the id
        ---> can do Pokemon.get_related('gym')
        -> makes related queries tricky
        -> I need to start building apps using aragorm ... so can work out
        what's required and what isn't.
        -> need a simple router ...
        --> sanic or quart

        """
        return Insert(
            table=cls,
            base='INSERT INTO {cls.Meta.tablename}',
        )

    @classmethod
    def update(cls, **columns) -> Update:
        """
        await Pokemon.update(name='raichu').where(
            Pokemon.name='pikachu'
        ).run()
        """
        columns_str = ','.join([
            f'{column} = {getattr(cls, column).format_value(value)}' for (
                column, value) in columns.items()])

        return Update(
            table=cls,
            base=f'UPDATE {cls.Meta.tablename} SET {columns_str}'
        )

    @classmethod
    def delete(cls, **columns) -> Delete:
        """
        await Pokemon.delete().where(Pokemon.name='weedle').run()

        DELETE FROM pokemon where name = 'weedle'
        """
        return Delete(
            table=cls,
            base=f'DELETE FROM {cls.Meta.tablename}'
        )

    @classmethod
    def create(cls) -> Create:
        """
        Create table, along with all columns.

        await Pokemon.create().run()
        """
        return Create(
            table=cls,
            base=f'CREATE TABLE "{cls.Meta.tablename}"'
        )

    @classmethod
    def create_without_columns(cls) -> Raw:
        """
        Create the table, but with no columns (useful for migrations).

        await Pokemon.create().run()
        """
        return Raw(
            table=cls,
            base=f'CREATE TABLE "{cls.Meta.tablename}"()'
        )

    @classmethod
    def drop(cls) -> Drop:
        """
        Drops the table.

        await Pokemon.drop().run()
        """
        return Drop(
            table=cls,
            base=f'DROP TABLE "{cls.Meta.tablename}"'
        )

    @classmethod
    def raw(cls, sql: str) -> Raw:
        """
        await Pokemon.raw('select * from foo')
        """
        return Raw(
            table=cls,
            base=sql
        )

    @classmethod
    def alter(cls) -> Alter:
        """
        await Pokemon.alter().rename(Pokemon.power, 'rating')
        """
        return Alter(
            table=cls,
            base=f'ALTER TABLE "{cls.Meta.tablename}"'
        )

    @classmethod
    def exists(cls):
        """
        This is tricky ... use it to check if a row exists ... not if the
        table exists.
        """
        return Exists(
            table=cls,
            base=''
        )

    @classmethod
    def table_exists(cls) -> TableExists:
        return TableExists(
            table=cls,
            base=(
                "SELECT EXISTS(SELECT * FROM information_schema.tables WHERE "
                f"table_name = '{cls.Meta.tablename}')"
            )
        )
