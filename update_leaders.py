""" A simple script to update the leaders table. """

from ProductionCode.data_accessor import DataAccessor


def main():
    data_accessor = DataAccessor()
    data_accessor._compute_leaders()


if __name__ == '__main__':
    main()