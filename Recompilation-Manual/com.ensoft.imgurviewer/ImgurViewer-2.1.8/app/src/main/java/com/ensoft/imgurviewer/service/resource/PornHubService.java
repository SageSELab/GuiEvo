package com.ensoft.imgurviewer.service.resource;

import android.net.Uri;
import android.text.TextUtils;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class PornHubService extends BasicVideoServiceSolver
{
	public static final String PORNHUB_DOMAIN = "pornhub.com";
	
	@Override
	public String getDomain()
	{
		return PORNHUB_DOMAIN;
	}
	
	@Override
	public String[] getDomainPath()
	{
		return new String[] { "/view_video.php?" };
	}
	
	@Override
	protected Map<String, String> getHeaders( Uri referer )
	{
		Map<String, String> headers = super.getHeaders( referer );
		headers.put( "Cookie", "platform=tv;" );
		return headers;
	}
	
	@Override
	public String[] getNeedleStart()
	{
		return new String[] {};
	}
	
	@Override
	public String[] getNeedleEnd()
	{
		return new String[] {};
	}
	
	private List<String> getJsVars(String mediaString)
	{
		ArrayList<String> list = new ArrayList<>();
		
		if ( mediaString != null )
		{
			String cleanString = mediaString.replaceAll( "[^:]//.*|/\\\\*((?!=*/)(?s:.))+\\\\*/", "" );
			String[] vars = cleanString.split( "\\+" );
			for ( String var : vars )
			{
				list.add( var.trim() );
			}
		}
		
		return list;
	}
	
	private String getJsVarValue(String response, String varName)
	{
		StringBuilder varValue = new StringBuilder();
		String varDefinition = String.format( "var %s=", varName );
		Pattern regex = Pattern.compile( String.format( "%s(.*?)\";", varDefinition ) );
		Matcher m = regex.matcher(response);
		
		if ( m.find() )
		{
			String varDeclaration = m.group();
			String varValues = varDeclaration.substring( varDefinition.length(), varDeclaration.length() - 1 );
			String[] values = varValues.split( "\\+" );
			
			for ( String val : values )
			{
				val = val.trim().replaceAll( "\"", "" );
				varValue.append( val );
			}
		}
		
		return varValue.toString();
	}
	
	private Map<String, String> extractUrls( String response )
	{
		HashMap<String, String> map = new HashMap<>(  );
		HashMap<String, String> res = new HashMap<>(  );
		ArrayList<String> list = new ArrayList<>();
		Pattern regex = Pattern.compile( "(var\\s+(?:media|quality)_.+)" );
		Matcher m = regex.matcher(response);
		while ( m.find() )
		{
			for ( int i = 0; i < m.groupCount(); i++ )
			{
				list.addAll( Arrays.asList( m.group( i ).split( ";" ) ) );
			}
		}
		
		for ( String var: list )
		{
			var = var.substring( 4 );
			String[] split = var.split( "=" );
			String valuePart = split[1];
			if ( split.length > 2 )
			{
				for ( int i = 2; i < split.length; i++ )
				{
					valuePart += "=" + split[i];
				}
			}
			valuePart = valuePart.replaceAll( "/\\*(?:(?!\\*/).)*?\\*/", "" )
				.trim()
				.replaceAll( "\"", "" );
			
			map.put( split[0], valuePart );
		}
		
		
		for ( Map.Entry<String, String> entry : map.entrySet() )
		{
			if ( entry.getKey().startsWith( "quality" ) || entry.getKey().startsWith( "media" ) )
			{
				String[] values = entry.getValue().split( "\\+" );
				StringBuilder solved = new StringBuilder();
				
				for ( String value : values )
				{
					value = value.trim().replaceAll( " \\+ ", "" );
					String newVal = map.get( value );
					if ( newVal != null )
					{
						newVal = newVal.trim().replaceAll( " \\+ ", "" );
						solved.append( newVal );
					}
				}
				
				entry.setValue( solved.toString() );
				
				res.put( entry.getKey(), entry.getValue() );
			}
		}
		
		return res;
	}
	
	@Override
	protected Uri getVideoUrlFromResponse( String response )
	{
		Map<String, String> vars = extractUrls( response );
		
		if ( !vars.isEmpty() )
		{
			int bestQuality = 0;
			String bestQualityUrl = "";
			for ( Map.Entry<String, String> entry : vars.entrySet() )
			{
				if ( entry.getKey().startsWith( "quality_" ) && !entry.getValue().isEmpty() )
				{
					int q = Integer.parseInt( entry.getKey().substring( 8 ).replace( "p", "" ) );
					
					if ( q > bestQuality )
					{
						bestQuality = q;
						bestQualityUrl = entry.getValue();
					}
				}
			}
			
			try
			{
				return Uri.parse( bestQualityUrl );
			}
			catch ( Exception ignored )
			{
				return null;
			}
		}
		else
		{
			List<String> mediaVars = getJsVars(getStringMatch( response, "var mediastring=", ";</script>" ));
			StringBuilder url = new StringBuilder();
			
			for ( String var : mediaVars )
			{
				url.append( getJsVarValue( response, var ) );
			}
			
			return !url.toString().isEmpty() ? Uri.parse( url.toString() ) : null;
		}
	}
}
