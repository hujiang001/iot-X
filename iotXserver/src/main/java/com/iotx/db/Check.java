package com.iotx.db;

import java.awt.EventQueue;
import java.util.Arrays;

public class Check {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		System.out.println("current path:" + System.getProperty("user.dir"));
		EventQueue.invokeLater(new Runnable() {
			public void run() {
				try {
					DBConfigWindow window = new DBConfigWindow();
					window.getFrame().setVisible(true);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});

	}

}
