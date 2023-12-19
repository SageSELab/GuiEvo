package xyz.zedler.patrick.grocy.model;

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

import android.os.Parcel;
import android.os.Parcelable;

import androidx.annotation.NonNull;

import java.util.ArrayList;

public class MissingBatchItem implements Parcelable {

    private String productName, barcodes;
    private String defaultStoreId;
    private String productId;
    private String lastPrice;
    private int defaultBestBeforeDays, defaultLocationId = -1, isOnServer = 0;
    private boolean isDefaultBestBeforeDaysSet = false;
    private ArrayList<BatchPurchaseEntry> batchPurchaseEntries = new ArrayList<>();

    public MissingBatchItem(
            String productName,
            String barcodes
    ) {
        this.productName = productName;
        this.barcodes = barcodes;
    }

    private MissingBatchItem(Parcel parcel) {
        productName = parcel.readString();
        barcodes = parcel.readString();
        defaultLocationId = parcel.readInt();
        defaultBestBeforeDays = parcel.readInt();
        defaultStoreId = parcel.readString();
        batchPurchaseEntries = new ArrayList<>();
        parcel.readList(batchPurchaseEntries, BatchPurchaseEntry.class.getClassLoader());
        isOnServer = parcel.readInt();
        productId = parcel.readString();
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeString(productName);
        dest.writeString(barcodes);
        dest.writeInt(defaultLocationId);
        dest.writeInt(defaultBestBeforeDays);
        dest.writeString(defaultStoreId);
        dest.writeList(batchPurchaseEntries);
        dest.writeInt(isOnServer);
        dest.writeString(productId);
    }

    public static final Creator<MissingBatchItem> CREATOR = new Creator<MissingBatchItem>() {

        @Override
        public MissingBatchItem createFromParcel(Parcel in) {
            return new MissingBatchItem(in);
        }

        @Override
        public MissingBatchItem[] newArray(int size) {
            return new MissingBatchItem[size];
        }
    };

    public String getProductName() {
        return productName;
    }

    public void setProductName(String productName) {
        this.productName = productName;
    }

    public String getBarcodes() {
        return barcodes;
    }

    public void setBarcodes(String barcodes) {
        this.barcodes = barcodes;
    }

    public int getDefaultBestBeforeDays() {
        return defaultBestBeforeDays;
    }

    public boolean getIsDefaultBestBeforeDaysSet() {
        return isDefaultBestBeforeDaysSet;
    }

    public void setDefaultBestBeforeDays(int defaultBestBeforeDays) {
        this.defaultBestBeforeDays = defaultBestBeforeDays;
        isDefaultBestBeforeDaysSet = true;
    }

    public int getDefaultLocationId() {
        return defaultLocationId;
    }

    public void setDefaultLocationId(int defaultLocationId) {
        this.defaultLocationId = defaultLocationId;
    }

    public String getDefaultStoreId() {
        return defaultStoreId;
    }

    public void setDefaultStoreId(String defaultStoreId) {
        this.defaultStoreId = defaultStoreId;
    }

    public int getPurchaseEntriesSize() {
        return batchPurchaseEntries.size();
    }

    public ArrayList<BatchPurchaseEntry> getPurchaseEntries() {
        return batchPurchaseEntries;
    }

    public void addPurchaseEntry(BatchPurchaseEntry batchPurchaseEntry) {
        batchPurchaseEntries.add(batchPurchaseEntry);
    }

    public boolean getIsOnServer() {
        return isOnServer == 1;
    }

    public void setIsOnServer(boolean isOnServer) {
        this.isOnServer = isOnServer ? 1 : 0;
    }

    public String getProductId() {
        return productId;
    }

    public void setProductId(int productId) {
        this.productId = String.valueOf(productId);
    }

    public String getLastPrice() {
        return lastPrice;
    }

    public void setLastPrice(String lastPrice) {
        this.lastPrice = lastPrice;
    }

    @Override
    public int describeContents() {
        return 0;
    }

    @NonNull
    @Override
    public String toString() {
        return "MissingBatchItem(" + productName + ")";
    }
}
