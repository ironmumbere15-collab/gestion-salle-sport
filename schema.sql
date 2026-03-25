CREATE TABLE abonnes (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL,
    email TEXT NOT NULL,
    date_fin DATE NOT NULL,
    notifie INTEGER DEFAULT 0
);

-- Exemple de test (à modifier plus tard)
INSERT INTO abonnes (nom, email, date_fin) 
VALUES ('Jean Dupont', 'jean.dupont@email.com', '2024-06-01');
