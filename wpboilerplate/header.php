<?php
/**
 * The header for our theme.
 *
 * Displays all of the <head> section and everything up till <div id="content">
 *
 * @package boilerplate
 */
?><!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo( 'charset' ); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title><?php wp_title( '|', true, 'right' ); ?></title>
<link rel="profile" href="http://gmpg.org/xfn/11">
<link rel="pingback" href="<?php bloginfo( 'pingback_url' ); ?>">
<?php wp_head(); ?>
</head>

<body <?php body_class(); ?>>
	<div class="page">
		<header class="site-header">
			<img src="http://i.imgur.com/5PTFmgW.jpg" alt="">
			<div class="site-title">
				<h1><a href="<?php echo esc_url( home_url( '/' ) ); ?>" rel="home"><?php bloginfo( 'name' ); ?></a></h1>
				<h2><?php bloginfo( 'description' ); ?></h2>
			</div>
			<nav role="navigation">
				<?php wp_nav_menu( array( 'theme_location' => 'primary' ) ); ?>
			</nav>
		</header>
		<div class="site-content">