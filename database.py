from src.database import *

def main():
    table = DatabaseTable(
        'usersv2',
        [
            DatabaseColumn(
                name='id',
                type=int,
                primary_key=True,
            ),
            DatabaseColumn(
                name='name',
                type=str,
                default='no name provided'
            ),
        ]
    )
    
    configuration = DatabaseConfig()
    configuration.add_table(table)
    
    database = Database('test.db')
    
    database.add_configuration(configuration)
    
    database.update_tables()

if __name__ == '__main__':
    main()
