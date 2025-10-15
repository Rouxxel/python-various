package card_game;

import logic_class.WarGame;
import players_class.Player;
import card_n_deck.Card;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;

public class WarGameGUI extends JFrame {
    private WarGame game;
    private JLabel player1Label, player2Label, player1CardsLabel, player2CardsLabel;
    private JLabel player1CardLabel, player2CardLabel, roundLabel, statusLabel;
    private JButton playRoundButton, saveButton, loadButton, newGameButton;
    private JTextArea gameLogArea;
    private JScrollPane scrollPane;
    
    public WarGameGUI() {
        game = new WarGame();
        initializeGUI();
    }
    
    private void initializeGUI() {
        setTitle("WAR Card Game");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout());
        
        // Create main panels
        createTopPanel();
        createCenterPanel();
        createBottomPanel();
        
        // Set window properties
        setSize(800, 600);
        setLocationRelativeTo(null);
        setResizable(true);
        
        // Start with new game dialog
        showNewGameDialog();
    }
    
    private void createTopPanel() {
        JPanel topPanel = new JPanel(new GridLayout(2, 4, 10, 5));
        topPanel.setBorder(BorderFactory.createTitledBorder("Game Status"));
        
        // Player info labels
        player1Label = new JLabel("Player 1: Not Set", SwingConstants.CENTER);
        player2Label = new JLabel("Player 2: Not Set", SwingConstants.CENTER);
        player1CardsLabel = new JLabel("Cards: 0", SwingConstants.CENTER);
        player2CardsLabel = new JLabel("Cards: 0", SwingConstants.CENTER);
        
        // Current cards
        player1CardLabel = new JLabel("No Card", SwingConstants.CENTER);
        player2CardLabel = new JLabel("No Card", SwingConstants.CENTER);
        roundLabel = new JLabel("Round: 0", SwingConstants.CENTER);
        statusLabel = new JLabel("Ready to Start", SwingConstants.CENTER);
        
        // Style labels
        Font labelFont = new Font("Arial", Font.BOLD, 12);
        player1Label.setFont(labelFont);
        player2Label.setFont(labelFont);
        player1Label.setForeground(Color.BLUE);
        player2Label.setForeground(Color.RED);
        
        topPanel.add(player1Label);
        topPanel.add(player2Label);
        topPanel.add(roundLabel);
        topPanel.add(statusLabel);
        topPanel.add(player1CardsLabel);
        topPanel.add(player2CardsLabel);
        topPanel.add(player1CardLabel);
        topPanel.add(player2CardLabel);
        
        add(topPanel, BorderLayout.NORTH);
    }
    
    private void createCenterPanel() {
        JPanel centerPanel = new JPanel(new BorderLayout());
        
        // Game log area
        gameLogArea = new JTextArea(15, 50);
        gameLogArea.setEditable(false);
        gameLogArea.setFont(new Font("Monospaced", Font.PLAIN, 12));
        scrollPane = new JScrollPane(gameLogArea);
        scrollPane.setBorder(BorderFactory.createTitledBorder("Game Log"));
        
        centerPanel.add(scrollPane, BorderLayout.CENTER);
        add(centerPanel, BorderLayout.CENTER);
        
        // Add welcome message
        appendToLog("🃏 Welcome to WAR Card Game! 🃏");
        appendToLog("Click 'New Game' to start playing.");
    }
    
    private void createBottomPanel() {
        JPanel bottomPanel = new JPanel(new FlowLayout());
        
        // Create buttons
        newGameButton = new JButton("New Game");
        playRoundButton = new JButton("Play Round");
        saveButton = new JButton("Save Game");
        loadButton = new JButton("Load Game");
        
        // Style buttons
        Dimension buttonSize = new Dimension(120, 30);
        newGameButton.setPreferredSize(buttonSize);
        playRoundButton.setPreferredSize(buttonSize);
        saveButton.setPreferredSize(buttonSize);
        loadButton.setPreferredSize(buttonSize);
        
        // Initially disable game buttons
        playRoundButton.setEnabled(false);
        saveButton.setEnabled(false);
        
        // Add action listeners
        newGameButton.addActionListener(e -> showNewGameDialog());
        playRoundButton.addActionListener(e -> playRound());
        saveButton.addActionListener(e -> saveGame());
        loadButton.addActionListener(e -> loadGame());
        
        bottomPanel.add(newGameButton);
        bottomPanel.add(playRoundButton);
        bottomPanel.add(saveButton);
        bottomPanel.add(loadButton);
        
        add(bottomPanel, BorderLayout.SOUTH);
    }
    
    private void showNewGameDialog() {
        JDialog dialog = new JDialog(this, "New Game Setup", true);
        dialog.setLayout(new GridLayout(4, 2, 10, 10));
        dialog.setSize(300, 200);
        dialog.setLocationRelativeTo(this);
        
        JLabel nameLabel = new JLabel("Your Name:");
        JTextField nameField = new JTextField("Player 1");
        
        JLabel modeLabel = new JLabel("Game Mode:");
        JComboBox<String> modeCombo = new JComboBox<>(new String[]{"vs Computer", "vs Human Player"});
        
        JButton startButton = new JButton("Start Game");
        JButton cancelButton = new JButton("Cancel");
        
        startButton.addActionListener(e -> {
            String playerName = nameField.getText().trim();
            if (playerName.isEmpty()) playerName = "Player 1";
            
            boolean vsComputer = modeCombo.getSelectedIndex() == 0;
            
            game = new WarGame();
            game.initializeGame(playerName, vsComputer);
            
            updateGUI();
            playRoundButton.setEnabled(true);
            saveButton.setEnabled(true);
            
            appendToLog("\n=== NEW GAME STARTED ===");
            appendToLog("Player 1: " + game.getPlayer1().getName());
            appendToLog("Player 2: " + game.getPlayer2().getName());
            appendToLog("Each player has 26 cards. Let the battle begin!");
            
            dialog.dispose();
        });
        
        cancelButton.addActionListener(e -> dialog.dispose());
        
        dialog.add(nameLabel);
        dialog.add(nameField);
        dialog.add(modeLabel);
        dialog.add(modeCombo);
        dialog.add(new JLabel()); // Empty space
        dialog.add(new JLabel()); // Empty space
        dialog.add(startButton);
        dialog.add(cancelButton);
        
        dialog.setVisible(true);
    }
    
    private void playRound() {
        if (game.isGameOver()) {
            JOptionPane.showMessageDialog(this, "Game is over! Start a new game.");
            return;
        }
        
        // Capture game state before round
        int oldRound = game.getRoundNumber();
        
        // Play the round (this will update the game state)
        game.playRound();
        
        // Update GUI
        updateGUI();
        
        // Show round result
        if (game.isGameOver()) {
            appendToLog("\n🎉 GAME OVER! 🎉");
            appendToLog(game.getWinner().getName() + " wins the game!");
            appendToLog("Total rounds: " + game.getRoundNumber());
            
            playRoundButton.setEnabled(false);
            saveButton.setEnabled(false);
            
            int result = JOptionPane.showConfirmDialog(this, 
                game.getWinner().getName() + " wins!\nWould you like to start a new game?",
                "Game Over", JOptionPane.YES_NO_OPTION);
            
            if (result == JOptionPane.YES_OPTION) {
                showNewGameDialog();
            }
        }
    }
    
    private void saveGame() {
        JFileChooser fileChooser = new JFileChooser();
        fileChooser.setDialogTitle("Save Game");
        fileChooser.setSelectedFile(new File("wargame_save.json"));
        
        int result = fileChooser.showSaveDialog(this);
        if (result == JFileChooser.APPROVE_OPTION) {
            String filename = fileChooser.getSelectedFile().getAbsolutePath();
            if (!filename.endsWith(".json")) {
                filename += ".json";
            }
            
            game.saveGame(filename);
            appendToLog("Game saved to: " + filename);
            JOptionPane.showMessageDialog(this, "Game saved successfully!");
        }
    }
    
    private void loadGame() {
        JFileChooser fileChooser = new JFileChooser();
        fileChooser.setDialogTitle("Load Game");
        
        int result = fileChooser.showOpenDialog(this);
        if (result == JFileChooser.APPROVE_OPTION) {
            String filename = fileChooser.getSelectedFile().getAbsolutePath();
            
            if (game.loadGame(filename)) {
                updateGUI();
                playRoundButton.setEnabled(true);
                saveButton.setEnabled(true);
                
                appendToLog("\n=== GAME LOADED ===");
                appendToLog("Player 1: " + game.getPlayer1().getName() + " (" + game.getPlayer1().getHandSize() + " cards)");
                appendToLog("Player 2: " + game.getPlayer2().getName() + " (" + game.getPlayer2().getHandSize() + " cards)");
                appendToLog("Round: " + game.getRoundNumber());
                
                JOptionPane.showMessageDialog(this, "Game loaded successfully!");
            } else {
                JOptionPane.showMessageDialog(this, "Failed to load game!", "Error", JOptionPane.ERROR_MESSAGE);
            }
        }
    }
    
    private void updateGUI() {
        if (game.getPlayer1() != null && game.getPlayer2() != null) {
            player1Label.setText("Player 1: " + game.getPlayer1().getName());
            player2Label.setText("Player 2: " + game.getPlayer2().getName());
            player1CardsLabel.setText("Cards: " + game.getPlayer1().getHandSize());
            player2CardsLabel.setText("Cards: " + game.getPlayer2().getHandSize());
            roundLabel.setText("Round: " + game.getRoundNumber());
            
            if (game.isGameOver()) {
                statusLabel.setText("GAME OVER - " + game.getWinner().getName() + " Wins!");
                statusLabel.setForeground(Color.RED);
            } else {
                statusLabel.setText("Game in Progress");
                statusLabel.setForeground(Color.GREEN);
            }
        }
    }
    
    private void appendToLog(String message) {
        gameLogArea.append(message + "\n");
        gameLogArea.setCaretPosition(gameLogArea.getDocument().getLength());
    }
    
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            try {
                UIManager.setLookAndFeel(UIManager.getSystemLookAndFeel());
            } catch (Exception e) {
                e.printStackTrace();
            }
            
            new WarGameGUI().setVisible(true);
        });
    }
}