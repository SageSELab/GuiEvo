package com.readrops.readropslibrary.utils;

import java.io.InputStream;
import java.util.Scanner;

public final class LibUtils {

    public static final String RSS_DEFAULT_CONTENT_TYPE = "application/rss+xml";
    public static final String RSS_TEXT_CONTENT_TYPE = "text/xml";
    public static final String RSS_APPLICATION_CONTENT_TYPE = "application/xml";
    public static final String ATOM_CONTENT_TYPE = "application/atom+xml";
    public static final String JSON_CONTENT_TYPE = "application/json";
    public static final String HTML_CONTENT_TYPE = "text/html";

    public static final String CONTENT_TYPE_HEADER = "content-type";
    public static final String ETAG_HEADER = "ETag";
    public static final String IF_NONE_MATCH_HEADER = "If-None-Match";
    public static final String LAST_MODIFIED_HEADER = "Last-Modified";
    public static final String IF_MODIFIED_HEADER = "If-Modified-Since";

    public static final int HTTP_UNPROCESSABLE = 422;
    public static final int HTTP_NOT_FOUND = 404;
    public static final int HTTP_CONFLICT = 409;


    public static String inputStreamToString(InputStream input) {
        Scanner scanner = new Scanner(input).useDelimiter("\\A");
        return scanner.hasNext() ? scanner.next() : "";
    }



}
