package com.iotx.db;

import java.awt.EventQueue;

import javax.swing.JFrame;
import javax.swing.JOptionPane;
import javax.swing.JPasswordField;

import java.awt.GridBagLayout;
import javax.swing.JLabel;
import java.awt.GridBagConstraints;
import java.awt.GridLayout;
import java.awt.BorderLayout;
import javax.swing.JPanel;
import javax.swing.border.TitledBorder;
import javax.swing.JTextField;
import java.awt.Insets;
import javax.swing.JButton;
import java.awt.FlowLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.Arrays;

public class DBConfigWindow {

	private JFrame frame;
	private JTextField textIP;
	private JTextField textPort;
	private JTextField textUserName;
	private JPasswordField textPwd;
	private JButton btnCheck;
	private JButton btnExport;

	/**
	 * Launch the application.
	 */
	public static void main(String[] args) {
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

	/**
	 * Create the application.
	 */
	public DBConfigWindow() {
		initialize();
		addActionListeners();
	}

	/**
	 * Initialize the contents of the frame.
	 */
	private void initialize() {
		frame = new JFrame("Database Configuration");
		getFrame().setBounds(100, 100, 450, 300);
		getFrame().setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		getFrame().getContentPane().setLayout(new BorderLayout(0, 0));
		
		JPanel pCenter = new JPanel();
		getFrame().getContentPane().add(pCenter, BorderLayout.CENTER);
		pCenter.setLayout(new FlowLayout(FlowLayout.CENTER));
		
		JPanel panelInCenter = new JPanel();
		pCenter.add(panelInCenter);
		GridBagLayout gbl_panelInCenter = new GridBagLayout();
		gbl_panelInCenter.columnWidths = new int[]{0, 0, 0};
		gbl_panelInCenter.rowHeights = new int[]{0, 0, 0, 0, 0};
		gbl_panelInCenter.columnWeights = new double[]{1.0, 1.0, Double.MIN_VALUE};
		gbl_panelInCenter.rowWeights = new double[]{0.0, 0.0, 0.0, 0.0, Double.MIN_VALUE};
		panelInCenter.setLayout(gbl_panelInCenter);
		
		JLabel lblIpAddress = new JLabel("IP ADDRESS");
		GridBagConstraints gbc_lblIpAddress = new GridBagConstraints();
		gbc_lblIpAddress.anchor = GridBagConstraints.EAST;
		gbc_lblIpAddress.insets = new Insets(5, 5, 5, 5);
		gbc_lblIpAddress.gridx = 0;
		gbc_lblIpAddress.gridy = 0;
		panelInCenter.add(lblIpAddress, gbc_lblIpAddress);
		
		textIP = new JTextField();
		GridBagConstraints gbc_textIP = new GridBagConstraints();
		gbc_textIP.insets = new Insets(5, 5, 5, 5);
		gbc_textIP.fill = GridBagConstraints.HORIZONTAL;
		gbc_textIP.gridx = 1;
		gbc_textIP.gridy = 0;
		panelInCenter.add(textIP, gbc_textIP);
		textIP.setColumns(10);
		
		textPort = new JTextField();
		textPort.setText("");
		GridBagConstraints gbc_textPort = new GridBagConstraints();
		gbc_textPort.insets = new Insets(5, 5, 5, 5);
		gbc_textPort.fill = GridBagConstraints.HORIZONTAL;
		gbc_textPort.gridx = 1;
		gbc_textPort.gridy = 1;
		panelInCenter.add(textPort, gbc_textPort);
		textPort.setColumns(10);
		
		textUserName = new JTextField();
		textUserName.setText("");
		GridBagConstraints gbc_textUserName = new GridBagConstraints();
		gbc_textUserName.insets = new Insets(5, 5, 5, 5);
		gbc_textUserName.fill = GridBagConstraints.HORIZONTAL;
		gbc_textUserName.gridx = 1;
		gbc_textUserName.gridy = 2;
		panelInCenter.add(textUserName, gbc_textUserName);
		textUserName.setColumns(10);
		
		JLabel lblPasswrd = new JLabel("PASSWRD");
		GridBagConstraints gbc_lblPasswrd = new GridBagConstraints();
		gbc_lblPasswrd.anchor = GridBagConstraints.EAST;
		gbc_lblPasswrd.insets = new Insets(5, 5, 5, 5);
		gbc_lblPasswrd.gridx = 0;
		gbc_lblPasswrd.gridy = 3;
		panelInCenter.add(lblPasswrd, gbc_lblPasswrd);
		
		JLabel lblUserName = new JLabel("USER NAME");
		GridBagConstraints gbc_lblUserName = new GridBagConstraints();
		gbc_lblUserName.anchor = GridBagConstraints.EAST;
		gbc_lblUserName.insets = new Insets(5, 5, 5, 5);
		gbc_lblUserName.gridx = 0;
		gbc_lblUserName.gridy = 2;
		panelInCenter.add(lblUserName, gbc_lblUserName);
		
		JLabel lblPort = new JLabel("PORT");
		GridBagConstraints gbc_lblPort = new GridBagConstraints();
		gbc_lblPort.anchor = GridBagConstraints.EAST;
		gbc_lblPort.insets = new Insets(5, 5, 5, 5);
		gbc_lblPort.gridx = 0;
		gbc_lblPort.gridy = 1;
		panelInCenter.add(lblPort, gbc_lblPort);
		
		textPwd = new JPasswordField();
		textPwd.setText("");
		GridBagConstraints gbc_textPwd = new GridBagConstraints();
		gbc_textPwd.insets = new Insets(5, 5, 5, 5);
		gbc_textPwd.fill = GridBagConstraints.HORIZONTAL;
		gbc_textPwd.gridx = 1;
		gbc_textPwd.gridy = 3;
		panelInCenter.add(textPwd, gbc_textPwd);
		textPwd.setColumns(10);
		
		JPanel pBottom = new JPanel();
		pBottom.setBorder(new TitledBorder(null, "", TitledBorder.LEADING, TitledBorder.TOP, null, null));
		getFrame().getContentPane().add(pBottom, BorderLayout.SOUTH);
		pBottom.setLayout(new FlowLayout(FlowLayout.CENTER, 5, 5));
		
		JPanel panelInBottom = new JPanel();
		pBottom.add(panelInBottom);
		GridBagLayout gbl_panelInBottom = new GridBagLayout();
		gbl_panelInBottom.columnWidths = new int[]{0, 0, 0};
		gbl_panelInBottom.rowHeights = new int[]{0, 0, 0};
		gbl_panelInBottom.columnWeights = new double[]{0.0, 0.0, Double.MIN_VALUE};
		gbl_panelInBottom.rowWeights = new double[]{0.0, 0.0, Double.MIN_VALUE};
		panelInBottom.setLayout(gbl_panelInBottom);
		
		btnCheck = new JButton("CHECK");
		GridBagConstraints gbc_btnCheck = new GridBagConstraints();
		gbc_btnCheck.insets = new Insets(5, 5, 5, 5);
		gbc_btnCheck.gridx = 0;
		gbc_btnCheck.gridy = 0;
		panelInBottom.add(btnCheck, gbc_btnCheck);
		
		btnExport = new JButton("EXPORT");
		GridBagConstraints gbc_btnExport = new GridBagConstraints();
		gbc_btnExport.insets = new Insets(5, 5, 5, 5);
		gbc_btnExport.gridx = 1;
		gbc_btnExport.gridy = 0;
		panelInBottom.add(btnExport, gbc_btnExport);
	}
	
	private void addActionListeners() {
		btnCheck.addActionListener(new ActionListener() {
			
			@Override
			public void actionPerformed(ActionEvent e) {
				try {
					DBCheckUtils.check(textIP.getText().trim(),
							           textPort.getText().trim(),
							           textUserName.getText().trim(),
							           new String(textPwd.getPassword()));
					JOptionPane.showMessageDialog(null, "CHECK DONE,SUCCESS");
				}catch (Exception ex) {
					//TODO: add the exception stack to log
					JOptionPane.showMessageDialog(null, "Can Not Connect To Mysql");
				}
			}
		});
		
		btnExport.addActionListener(new ActionListener() {
			
			@Override
			public void actionPerformed(ActionEvent e) {
				try {
					DBCheckUtils.export(textIP.getText().trim(),
					                    textPort.getText().trim(),
					                    textUserName.getText().trim(),
					                    new String(textPwd.getPassword()));
					JOptionPane.showMessageDialog(null, "EXPORT DONE,SUCCESS!");
				}catch (Exception ex) {
					//TODO: add the exception stack to log
					JOptionPane.showMessageDialog(null, "Can Not Export This Connection");
				}
			}
		});
		
	}

	public JFrame getFrame() {
		return frame;
	}

}
