package xyz.zedler.patrick.grocy.dao;

/*
    This file is part of Grocy Android.

    Grocy Android is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Grocy Android is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Grocy Android.  If not, see <http://www.gnu.org/licenses/>.

    Copyright 2020 by Patrick Zedler & Dominic Zedler
*/

import androidx.room.Dao;
import androidx.room.Delete;
import androidx.room.Insert;
import androidx.room.OnConflictStrategy;
import androidx.room.Query;

import java.util.List;

import xyz.zedler.patrick.grocy.model.QuantityUnit;

@Dao
public interface QuantityUnitDao {
    @Query("SELECT * FROM quantity_unit_table")
    List<QuantityUnit> getAll();

    @Query("SELECT COUNT(*) FROM quantity_unit_table")
    int count();

    @Insert
    void insertAll(List<QuantityUnit> quantityUnits);

    @Insert(onConflict = OnConflictStrategy.IGNORE)
    void insert(QuantityUnit quantityUnit);

    @Delete
    void delete(QuantityUnit quantityUnit);

    @Query("DELETE FROM quantity_unit_table")
    void deleteAll();

}
