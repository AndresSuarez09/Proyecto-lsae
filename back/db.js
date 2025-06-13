require('dotenv').config();  //cargar variables del .env
console.log('Usuario:', process.env.DB_USER);
console.log('Contraseña:', process.env.DB_PASSWORD);

const { Pool } = require('pg');

// Create a new Pool instance to manage database connections
const pool = new Pool({
    user: process.env.DB_USER,          // PostgreSQL username
    host: process.env.DB_HOST,      // Database host
    database: process.env.DB_NAME, // Database name
    password: process.env.DB_PASSWORD, // PostgreSQL password
    port: process.env.DB_PORT,             // PostgreSQL port (default: 5432)
    ssl: { rejectUnauthorized: false }
});

// Test the database connection
pool.query('SELECT NOW()', (err, res) => {
    if (err) {
        console.error('Error connecting to the database:', err);
    } else {
        console.log('Database connection successful:', res.rows[0]);
    }
});

// Export the pool object to be used in other files
module.exports = pool;