package com.readrops.readropslibrary.services.nextcloudnews;

import android.content.res.Resources;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.readrops.readropslibrary.services.API;
import com.readrops.readropslibrary.services.Credentials;
import com.readrops.readropslibrary.services.SyncType;
import com.readrops.readropslibrary.services.nextcloudnews.json.NextNewsFeed;
import com.readrops.readropslibrary.services.nextcloudnews.json.NextNewsFeeds;
import com.readrops.readropslibrary.services.nextcloudnews.json.NextNewsFolder;
import com.readrops.readropslibrary.services.nextcloudnews.json.NextNewsFolders;
import com.readrops.readropslibrary.services.nextcloudnews.json.NextNewsItemIds;
import com.readrops.readropslibrary.services.nextcloudnews.json.NextNewsItems;
import com.readrops.readropslibrary.services.nextcloudnews.json.NextNewsRenameFeed;
import com.readrops.readropslibrary.services.nextcloudnews.json.NextNewsUser;
import com.readrops.readropslibrary.utils.ConflictException;
import com.readrops.readropslibrary.utils.LibUtils;
import com.readrops.readropslibrary.utils.UnknownFormatException;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import retrofit2.Response;

public class NextNewsAPI extends API<NextNewsService> {

    private static final String TAG = NextNewsAPI.class.getSimpleName();

    public NextNewsAPI(Credentials credentials) {
        super(credentials, NextNewsService.class, NextNewsService.END_POINT);
    }

    public NextNewsUser login() throws IOException {
        Response<NextNewsUser> response = api.getUser().execute();

        if (!response.isSuccessful())
            return null;

        return response.body();
    }

    public @Nullable
    NextNewsFeeds createFeed(String url, int folderId)
            throws IOException, UnknownFormatException {
        Response<NextNewsFeeds> response = api.createFeed(url, folderId).execute();

        if (!response.isSuccessful()) {
            if (response.code() == LibUtils.HTTP_UNPROCESSABLE)
                throw new UnknownFormatException();
            else
                return null;
        }

        return response.body();
    }

    public NextNewsSyncResult sync(@NonNull SyncType syncType, @Nullable NextNewsSyncData data) throws IOException {
        NextNewsSyncResult syncResult = new NextNewsSyncResult();
        switch (syncType) {
            case INITIAL_SYNC:
                initialSync(syncResult);
                break;
            case CLASSIC_SYNC:
                if (data == null)
                    throw new NullPointerException("NextNewsSyncData can't be null");

                classicSync(syncResult, data);
                break;
        }

        return syncResult;
    }

    private void initialSync(NextNewsSyncResult syncResult) throws IOException {
        getFeedsAndFolders(syncResult);

        Response<NextNewsItems> itemsResponse = api.getItems(3, false, -1).execute();
        NextNewsItems itemList = itemsResponse.body();

        if (!itemsResponse.isSuccessful())
            syncResult.setError(true);

        if (itemList != null)
            syncResult.setItems(itemList.getItems());
    }

    private void classicSync(NextNewsSyncResult syncResult, NextNewsSyncData data) throws IOException {
        putModifiedItems(data, syncResult);
        getFeedsAndFolders(syncResult);

        Response<NextNewsItems> itemsResponse = api.getNewItems(data.getLastModified(), 3).execute();
        NextNewsItems itemList = itemsResponse.body();

        if (!itemsResponse.isSuccessful())
            syncResult.setError(true);

        if (itemList != null)
            syncResult.setItems(itemList.getItems());
    }

    private void getFeedsAndFolders(NextNewsSyncResult syncResult) throws IOException {
        Response<NextNewsFeeds> feedResponse = api.getFeeds().execute();
        NextNewsFeeds feedList = feedResponse.body();

        if (!feedResponse.isSuccessful())
            syncResult.setError(true);

        Response<NextNewsFolders> folderResponse = api.getFolders().execute();
        NextNewsFolders folderList = folderResponse.body();

        if (!folderResponse.isSuccessful())
            syncResult.setError(true);

        if (folderList != null)
            syncResult.setFolders(folderList.getFolders());

        if (feedList != null)
            syncResult.setFeeds(feedList.getFeeds());

    }

    private void putModifiedItems(NextNewsSyncData data, NextNewsSyncResult syncResult) throws IOException {
        if (data.getReadItems().size() == 0 && data.getUnreadItems().size() == 0)
            return;

        Response readItemsResponse = api.setArticlesState(StateType.READ.name().toLowerCase(),
                new NextNewsItemIds(data.getReadItems())).execute();

        Response unreadItemsResponse = api.setArticlesState(StateType.UNREAD.toString().toLowerCase(),
                new NextNewsItemIds(data.getUnreadItems())).execute();

        if (!readItemsResponse.isSuccessful())
            syncResult.setError(true);

        if (!unreadItemsResponse.isSuccessful())
            syncResult.setError(true);
    }

    public @Nullable
    NextNewsFolders createFolder(NextNewsFolder folder) throws IOException, UnknownFormatException, ConflictException {
        Response<NextNewsFolders> foldersResponse = api.createFolder(folder).execute();

        if (foldersResponse.isSuccessful())
            return foldersResponse.body();
        else if (foldersResponse.code() == LibUtils.HTTP_UNPROCESSABLE)
            throw new UnknownFormatException();
        else if (foldersResponse.code() == LibUtils.HTTP_CONFLICT)
            throw new ConflictException();
        else
            return null;
    }

    public boolean deleteFolder(NextNewsFolder folder) throws IOException {
        Response response = api.deleteFolder(folder.getId()).execute();

        if (response.isSuccessful())
            return true;
        else if (response.code() == LibUtils.HTTP_NOT_FOUND)
            throw new Resources.NotFoundException();
        else
            return false;
    }

    public boolean renameFolder(NextNewsFolder folder) throws IOException, UnknownFormatException, ConflictException {
        Response response = api.renameFolder(folder.getId(), folder).execute();

        if (response.isSuccessful())
            return true;
        else {
            switch (response.code()) {
                case LibUtils.HTTP_NOT_FOUND:
                    throw new Resources.NotFoundException();
                case LibUtils.HTTP_UNPROCESSABLE:
                    throw new UnknownFormatException();
                case LibUtils.HTTP_CONFLICT:
                    throw new ConflictException();
                default:
                    return false;
            }
        }
    }

    public boolean deleteFeed(int feedId) throws IOException {
        Response response = api.deleteFeed(feedId).execute();

        if (response.isSuccessful())
            return true;
        else if (response.code() == LibUtils.HTTP_NOT_FOUND)
            throw new Resources.NotFoundException();
        else
            return false;
    }

    public boolean changeFeedFolder(NextNewsFeed feed) throws IOException {
        Map<String, Integer> folderIdMap = new HashMap<>();
        folderIdMap.put("folderId", feed.getFolderId());

        Response response = api.changeFeedFolder(feed.getId(), folderIdMap).execute();

        if (response.isSuccessful())
            return true;
        else if (response.code() == LibUtils.HTTP_NOT_FOUND)
            throw new Resources.NotFoundException();
        else
            return false;
    }

    public boolean renameFeed(NextNewsRenameFeed feed) throws IOException {
        Response response = api.renameFeed(feed.getId(), feed).execute();

        if (response.isSuccessful())
            return true;
        else if (response.code() == LibUtils.HTTP_NOT_FOUND)
            throw new Resources.NotFoundException();
        else
            return false;
    }

    public enum StateType {
        READ,
        UNREAD,
        STARRED,
        UNSTARRED
    }
}
