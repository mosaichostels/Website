<?php
define( 'WP_CACHE', true );


/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during the installation.
 * You don't have to use the web site, you can copy this file to "wp-config.php"
 * and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * Database settings
 * * Secret keys
 * * Database table prefix
 * * Localized language
 * * ABSPATH
 *
 * @link https://wordpress.org/support/article/editing-wp-config-php/
 *
 * @package WordPress
 */

// ** Database settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', 'u738123768_V6VvD' );

/** Database username */
define( 'DB_USER', 'u738123768_SK8cx' );

/** Database password */
define( 'DB_PASSWORD', 'QhU8iqOY8H' );

/** Database hostname */
define( 'DB_HOST', '127.0.0.1' );

/** Database charset to use in creating database tables. */
define( 'DB_CHARSET', 'utf8' );

/** The database collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', '' );

/**#@+
 * Authentication unique keys and salts.
 *
 * Change these to different unique phrases! You can generate these using
 * the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}.
 *
 * You can change these at any point in time to invalidate all existing cookies.
 * This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define( 'AUTH_KEY',          '~GAZZwrAn6Jt^f?Q[z2=]hXiLag#>htnk[vY`]TY)mF>s>:w`}s}tRHs1p~w@_Vx' );
define( 'SECURE_AUTH_KEY',   'RQ;;s# :T%vjtjU-]~_/q[(Z6lN&i=W4nQXj3PWyJG7bR%s6Orc;S[arjNDRuuhl' );
define( 'LOGGED_IN_KEY',     'Yq@OHD6O@&)mI?&P*CaIfO9|Bl5KzWfu+fu]=By_U&83{U`S}(CEN`QU20ohM]Vz' );
define( 'NONCE_KEY',         'b{<lWc`z]8|Bxs2?FmVmM7]Bbn5gq[L?}7Dh;Sf(-ZeL,SV-!L&@tjO(b+q1Edc1' );
define( 'AUTH_SALT',         '$`.GfA5Zgzw&wAg*EKinwY>hV#@u2>zVGzQoQE<X{sgfCYUiN&r~9X}p:EQS0ePl' );
define( 'SECURE_AUTH_SALT',  'vp.Kvy]vy;12&_gRGmN+!^A?[{6_pqGAjzl](rL7xA*8ZY(3/s#Bbug87P4wa$Bp' );
define( 'LOGGED_IN_SALT',    'x)Lm_5>N]K}(asyQr>lt+(/B8-!qH!:Y; y=ZFp1q!!8cYi4, y-{b`iFlsb7HG<' );
define( 'NONCE_SALT',        'Lhr4FlVh2>(f2eL2LeJ/T#~A3`*?MGbZaOT71kGPM~`]HLCEz/ kOFqbOZBuDZb^' );
define( 'WP_CACHE_KEY_SALT', 'h.r <~UC]cMC,cbC`kDUxd@lF&H[j#bf,jz33OX>U!Sm0#JONf@?MAQOtE!+I(vR' );


/**#@-*/

/**
 * WordPress database table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 */
$table_prefix = 'wp_';


/* Add any custom values between this line and the "stop editing" line. */



/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 *
 * For information on other constants that can be used for debugging,
 * visit the documentation.
 *
 * @link https://wordpress.org/support/article/debugging-in-wordpress/
 */
if ( ! defined( 'WP_DEBUG' ) ) {
	define( 'WP_DEBUG', false );
}

define( 'FS_METHOD', 'direct' );
define( 'COOKIEHASH', '0afb2b15ab050287ae31d4c222416df1' );
define( 'WP_AUTO_UPDATE_CORE', 'minor' );
/* That's all, stop editing! Happy publishing. */

/** Absolute path to the WordPress directory. */
if ( ! defined( 'ABSPATH' ) ) {
	define( 'ABSPATH', __DIR__ . '/' );
}

/** Sets up WordPress vars and included files. */
require_once ABSPATH . 'wp-settings.php';
