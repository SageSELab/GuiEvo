package com.readrops.app.database.entities;

import androidx.room.ColumnInfo;
import androidx.room.Entity;
import androidx.room.ForeignKey;
import androidx.room.PrimaryKey;

import org.joda.time.LocalDateTime;

import static androidx.room.ForeignKey.CASCADE;


@Entity
(foreignKeys = @ForeignKey(entity = Feed.class, parentColumns = "id", childColumns = "feed_id", onDelete = CASCADE))
public class Item implements Comparable<Item> {

    @PrimaryKey(autoGenerate = true)
    private int id;

    private String title;

    private String description;

    @ColumnInfo(name = "clean_description")
    private String cleanDescription;

    private String link;

    @ColumnInfo(name = "image_link")
    private String imageLink;

    private String author;

    @ColumnInfo(name = "pub_date")
    private LocalDateTime pubDate;

    private String content;

    @ColumnInfo(name = "feed_id", index = true)
    private int feedId;

    @ColumnInfo(index = true)
    private String guid;

    @ColumnInfo(name = "read_time")
    private double readTime;

    private boolean read;

    @ColumnInfo(name = "read_changed")
    private boolean readChanged;

    @ColumnInfo(name = "read_it_later")
    private boolean readItLater;

    private String remoteId;

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getCleanDescription() {
        return cleanDescription;
    }

    public void setCleanDescription(String cleanDescription) {
        this.cleanDescription = cleanDescription;
    }

    public String getLink() {
        return link;
    }

    public void setLink(String link) {
        this.link = link;
    }

    public String getImageLink() {
        return imageLink;
    }

    public void setImageLink(String imageLink) {
        this.imageLink = imageLink;
    }

    public String getAuthor() {
        return author;
    }

    public void setAuthor(String author) {
        this.author = author;
    }

    public LocalDateTime getPubDate() {
        return pubDate;
    }

    public void setPubDate(LocalDateTime pubDate) {
        this.pubDate = pubDate;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public String getGuid() {
        return guid;
    }

    public void setGuid(String guid) {
        this.guid = guid;
    }

    public int getFeedId() {
        return feedId;
    }

    public void setFeedId(int feedId) {
        this.feedId = feedId;
    }

    public boolean hasImage() {
        return getImageLink() != null;
    }

    public double getReadTime() {
        return readTime;
    }

    public void setReadTime(double readTime) {
        this.readTime = readTime;
    }

    public String getText() {
        if (content != null)
            return content;
        else
            return description;
    }

    public boolean isRead() {
        return read;
    }

    public void setRead(boolean read) {
        this.read = read;
    }

    public boolean isReadChanged() {
        return readChanged;
    }

    public void setReadChanged(boolean readChanged) {
        this.readChanged = readChanged;
    }

    public boolean isReadItLater() {
        return readItLater;
    }

    public void setReadItLater(boolean readItLater) {
        this.readItLater = readItLater;
    }

    public String getRemoteId() {
        return remoteId;
    }

    public void setRemoteId(String remoteId) {
        this.remoteId = remoteId;
    }

    @Override
    public int compareTo(Item o) {
        return this.pubDate.compareTo(o.getPubDate());
    }
}
