package com.iotx.db;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.sql.DriverManager;
import java.util.Properties;

public class DBCheckUtils {

	private static String mysqlDriver = "com.mysql.jdbc.Driver";
	private static String url;
	private static String dbCfgFile = "conf" + File.separator + "mysqlconnection.properties";
	private static String getUrl(String ip, String port, String user, String pass) {
		StringBuffer sb = new StringBuffer();
		sb.append("jdbc:mysql://address=(protocol=tcp)");
		sb.append("(host=").append(ip).append(")");
		sb.append("(port=").append(port).append(")");
		sb.append("?");
		if(sb.charAt(sb.length() - 1) != '&' && sb.charAt(sb.length() - 1) != '?') {
			sb.append("&");
		}
		sb.append("user=").append(user).append("&");
		sb.append("password=").append(pass);
		char c = sb.charAt(sb.length() - 1);
		if(c == '?' || c == '&') {
			sb.deleteCharAt(sb.length() - 1);
		}
		
		return sb.toString();
	}
	
	public static void check(String ip, String port, String user, String pass) throws Exception{
		
		try {
			url = getUrl(ip, port, user, pass);
			Class.forName(mysqlDriver);
			DriverManager.setLoginTimeout(15);
			DriverManager.getConnection(url, user, pass);
		}catch (Throwable e) {
			throw new Exception("check connection error!", e);
		}
	}
	
	public static void export(String ip, String port, String user, String pass) throws Exception{
		check(ip, port, user, pass);
		Properties properties = new Properties();
		OutputStream os = new FileOutputStream(dbCfgFile);
		properties.setProperty("url", url);
		properties.store(os, "this is the database connection for mysql only");
		os.close();
	}
	
	public static String readUrl() {
		Properties properties = new Properties();
		try {
			InputStream is = new FileInputStream(dbCfgFile);
			properties.load(is);
			String storedUrl = properties.getProperty("url");
			return storedUrl;
		} catch (Exception e) {
			//TODO: log this exception
			return "";
		}
		
	}
	public static void main(String args[]) {
		try {
			export("10.74.64.150", "3306", "root", "U_tywg_2013");
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		String str = readUrl();
		System.out.println(str);
	}
}
