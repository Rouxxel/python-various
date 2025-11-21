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
    
    // Card image labels
    private JLabel player1CardImageLabel, player2CardImageLabel;
    
    // Queue for typewriter effect
    private java.util.Queue<String> messageQueue = new java.util.LinkedList<>();
    private boolean isTyping = false;
    
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
        setSize(900, 750);
        setLocationRelativeTo(null);
        setResizable(true);
        
        // Start with new game dialog
        showNewGameDialog();
    }
    
    private void createTopPanel() {
        JPanel topPanel = new JPanel(new BorderLayout());
        
        // Status panel at the very top
        JPanel statusPanel = new JPanel(new GridLayout(1, 2, 10, 5));
        roundLabel = new JLabel("Round: 0", SwingConstants.CENTER);
        statusLabel = new JLabel("Ready to Start", SwingConstants.CENTER);
        Font statusFont = new Font("Arial", Font.BOLD, 14);
        roundLabel.setFont(statusFont);
        statusLabel.setFont(statusFont);
        statusPanel.add(roundLabel);
        statusPanel.add(statusLabel);
        
        // Card display panel
        JPanel cardPanel = new JPanel(new GridLayout(1, 2, 20, 10));
        cardPanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));
        
        // Player 1 card area
        JPanel player1Area = new JPanel(new BorderLayout());
        player1Area.setBorder(BorderFactory.createTitledBorder("Player 1"));
        player1Label = new JLabel("Not Set", SwingConstants.CENTER);
        player1CardsLabel = new JLabel("Cards: 0", SwingConstants.CENTER);
        player1CardLabel = new JLabel("No Card", SwingConstants.CENTER);
        player1CardImageLabel = new JLabel("", SwingConstants.CENTER);
        player1CardImageLabel.setPreferredSize(new Dimension(150, 200));
        player1CardImageLabel.setBorder(BorderFactory.createLineBorder(Color.BLUE, 2));
        
        Font labelFont = new Font("Arial", Font.BOLD, 12);
        player1Label.setFont(labelFont);
        player1Label.setForeground(Color.BLUE);
        
        JPanel p1Info = new JPanel(new GridLayout(3, 1));
        p1Info.add(player1Label);
        p1Info.add(player1CardsLabel);
        p1Info.add(player1CardLabel);
        
        player1Area.add(p1Info, BorderLayout.NORTH);
        player1Area.add(player1CardImageLabel, BorderLayout.CENTER);
        
        // Player 2 card area
        JPanel player2Area = new JPanel(new BorderLayout());
        player2Area.setBorder(BorderFactory.createTitledBorder("Player 2"));
        player2Label = new JLabel("Not Set", SwingConstants.CENTER);
        player2CardsLabel = new JLabel("Cards: 0", SwingConstants.CENTER);
        player2CardLabel = new JLabel("No Card", SwingConstants.CENTER);
        player2CardImageLabel = new JLabel("", SwingConstants.CENTER);
        player2CardImageLabel.setPreferredSize(new Dimension(150, 200));
        player2CardImageLabel.setBorder(BorderFactory.createLineBorder(Color.RED, 2));
        
        player2Label.setFont(labelFont);
        player2Label.setForeground(Color.RED);
        
        JPanel p2Info = new JPanel(new GridLayout(3, 1));
        p2Info.add(player2Label);
        p2Info.add(player2CardsLabel);
        p2Info.add(player2CardLabel);
        
        player2Area.add(p2Info, BorderLayout.NORTH);
        player2Area.add(player2CardImageLabel, BorderLayout.CENTER);
        
        cardPanel.add(player1Area);
        cardPanel.add(player2Area);
        
        topPanel.add(statusPanel, BorderLayout.NORTH);
        topPanel.add(cardPanel, BorderLayout.CENTER);
        
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
        
        // Play round and capture output for GUI
        int roundNum = game.getRoundNumber() + 1;
        appendToLog("\n=== Round " + roundNum + " ===");
        
        // Check if players have cards
        if (!game.getPlayer1().hasCards()) {
            endGameGUI(game.getPlayer2());
            return;
        }
        if (!game.getPlayer2().hasCards()) {
            endGameGUI(game.getPlayer1());
            return;
        }
        
        // Play cards
        Card card1 = game.getPlayer1().playCard();
        Card card2 = game.getPlayer2().playCard();
        
        appendToLog(game.getPlayer1().getName() + " plays: " + card1.get_card_face() + " (" + card1.get_card_value() + ")");
        appendToLog(game.getPlayer2().getName() + " plays: " + card2.get_card_face() + " (" + card2.get_card_value() + ")");
        
        player1CardLabel.setText(card1.get_card_face());
        player2CardLabel.setText(card2.get_card_face());
        
        // Display card images
        displayCardImage(card1, player1CardImageLabel);
        displayCardImage(card2, player2CardImageLabel);
        
        java.util.List<Card> cardsOnTable = new java.util.ArrayList<>();
        cardsOnTable.add(card1);
        cardsOnTable.add(card2);
        
        // Compare cards
        if (card1.get_card_value() > card2.get_card_value()) {
            appendToLog(game.getPlayer1().getName() + " wins the round!");
            game.getPlayer1().addCards(cardsOnTable);
        } else if (card2.get_card_value() > card1.get_card_value()) {
            appendToLog(game.getPlayer2().getName() + " wins the round!");
            game.getPlayer2().addCards(cardsOnTable);
        } else {
            appendToLog("WAR! Cards are equal!");
            handleWarGUI(cardsOnTable);
        }
        
        // Increment round counter manually since we're not using game.playRound()
        java.lang.reflect.Field roundField;
        try {
            roundField = game.getClass().getDeclaredField("roundNumber");
            roundField.setAccessible(true);
            roundField.setInt(game, roundNum);
        } catch (Exception e) {
            // Ignore reflection errors
        }
        
        // Show current status
        appendToLog(game.getPlayer1().getName() + ": " + game.getPlayer1().getHandSize() + " cards");
        appendToLog(game.getPlayer2().getName() + ": " + game.getPlayer2().getHandSize() + " cards");
        
        // Update GUI
        updateGUI();
        
        // Check for game over
        if (!game.getPlayer1().hasCards()) {
            endGameGUI(game.getPlayer2());
        } else if (!game.getPlayer2().hasCards()) {
            endGameGUI(game.getPlayer1());
        }
    }
    
    private void handleWarGUI(java.util.List<Card> cardsOnTable) {
        appendToLog("Starting WAR sequence...");
        
        // Each player puts down 2 face-down cards and 1 face-up
        for (int i = 0; i < 2; i++) {
            if (game.getPlayer1().hasCards()) {
                Card faceDown1 = game.getPlayer1().playCard();
                cardsOnTable.add(faceDown1);
                appendToLog(game.getPlayer1().getName() + " places a face-down card");
            }
            if (game.getPlayer2().hasCards()) {
                Card faceDown2 = game.getPlayer2().playCard();
                cardsOnTable.add(faceDown2);
                appendToLog(game.getPlayer2().getName() + " places a face-down card");
            }
        }
        
        // Check if players still have cards for face-up battle
        if (!game.getPlayer1().hasCards()) {
            appendToLog(game.getPlayer1().getName() + " runs out of cards during war!");
            endGameGUI(game.getPlayer2());
            return;
        }
        if (!game.getPlayer2().hasCards()) {
            appendToLog(game.getPlayer2().getName() + " runs out of cards during war!");
            endGameGUI(game.getPlayer1());
            return;
        }
        
        // Face-up cards
        Card warCard1 = game.getPlayer1().playCard();
        Card warCard2 = game.getPlayer2().playCard();
        cardsOnTable.add(warCard1);
        cardsOnTable.add(warCard2);
        
        appendToLog(game.getPlayer1().getName() + " war card: " + warCard1.get_card_face() + " (" + warCard1.get_card_value() + ")");
        appendToLog(game.getPlayer2().getName() + " war card: " + warCard2.get_card_face() + " (" + warCard2.get_card_value() + ")");
        
        player1CardLabel.setText("WAR: " + warCard1.get_card_face());
        player2CardLabel.setText("WAR: " + warCard2.get_card_face());
        
        // Display war card images
        displayCardImage(warCard1, player1CardImageLabel);
        displayCardImage(warCard2, player2CardImageLabel);
        
        // Compare war cards
        if (warCard1.get_card_value() > warCard2.get_card_value()) {
            appendToLog(game.getPlayer1().getName() + " wins the WAR!");
            game.getPlayer1().addCards(cardsOnTable);
        } else if (warCard2.get_card_value() > warCard1.get_card_value()) {
            appendToLog(game.getPlayer2().getName() + " wins the WAR!");
            game.getPlayer2().addCards(cardsOnTable);
        } else {
            appendToLog("Another WAR!");
            handleWarGUI(cardsOnTable); // Recursive war
        }
    }
    
    private void endGameGUI(Player winner) {
        appendToLog("\n🎉 GAME OVER! 🎉");
        appendToLog(winner.getName() + " wins the game!");
        appendToLog("Total rounds: " + game.getRoundNumber());
        
        // Set game over state using reflection
        try {
            java.lang.reflect.Field gameOverField = game.getClass().getDeclaredField("gameOver");
            gameOverField.setAccessible(true);
            gameOverField.setBoolean(game, true);
            
            java.lang.reflect.Field winnerField = game.getClass().getDeclaredField("winner");
            winnerField.setAccessible(true);
            winnerField.set(game, winner);
        } catch (Exception e) {
            // Ignore reflection errors
        }
        
        playRoundButton.setEnabled(false);
        saveButton.setEnabled(false);
        updateGUI();
        
        int result = JOptionPane.showConfirmDialog(this, 
            winner.getName() + " wins!\nWould you like to start a new game?",
            "Game Over", JOptionPane.YES_NO_OPTION);
        
        if (result == JOptionPane.YES_OPTION) {
            showNewGameDialog();
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
            player1Label.setText(game.getPlayer1().getName());
            player2Label.setText(game.getPlayer2().getName());
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
    
    private void displayCardImage(Card card, JLabel imageLabel) {
        if (card == null) {
            imageLabel.setIcon(null);
            imageLabel.setText("No Card");
            return;
        }
        
        // Convert card face to filename format
        // e.g., "Ace of Spades" -> "ace_of_spades.png"
        String cardFace = card.get_card_face().toLowerCase().replace(" ", "_");
        String imagePath = "src/resources/img/" + cardFace + ".png";
        
        try {
            ImageIcon cardIcon = new ImageIcon(imagePath);
            
            // Scale image to fit label
            Image img = cardIcon.getImage();
            Image scaledImg = img.getScaledInstance(150, 200, Image.SCALE_SMOOTH);
            imageLabel.setIcon(new ImageIcon(scaledImg));
            imageLabel.setText("");
        } catch (Exception e) {
            // If image not found, just show text
            imageLabel.setIcon(null);
            imageLabel.setText(card.get_card_face());
        }
    }
    
    private void appendToLog(String message) {
        synchronized (messageQueue) {
            messageQueue.offer(message);
            if (!isTyping) {
                processNextMessage();
            }
        }
    }
    
    private void processNextMessage() {
        synchronized (messageQueue) {
            if (messageQueue.isEmpty()) {
                isTyping = false;
                return;
            }
            
            isTyping = true;
            String message = messageQueue.poll();
            
            // Typewriter effect - display characters one by one
            new Thread(() -> {
                try {
                    for (int i = 0; i < message.length(); i++) {
                        final char c = message.charAt(i);
                        SwingUtilities.invokeLater(() -> {
                            gameLogArea.append(String.valueOf(c));
                            gameLogArea.setCaretPosition(gameLogArea.getDocument().getLength());
                        });
                        Thread.sleep(24); // 0.024 seconds per character (50ms)
                    }
                    // Add newline at the end
                    SwingUtilities.invokeLater(() -> {
                        gameLogArea.append("\n");
                        gameLogArea.setCaretPosition(gameLogArea.getDocument().getLength());
                    });
                    
                    // Process next message in queue
                    processNextMessage();
                    
                } catch (InterruptedException e) {
                    e.printStackTrace();
                    isTyping = false;
                }
            }).start();
        }
    }
    
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            try {
                UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
            } catch (Exception e) {
                e.printStackTrace();
            }
            
            new WarGameGUI().setVisible(true);
        });
    }
}