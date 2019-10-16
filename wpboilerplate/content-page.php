<?php
/**
 * The template used for displaying page content in page.php
 *
 * @package boiletplate
 */
?>

<article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
	<header>
		<?php the_title( '<h1 class="page-title">', '</h1>' ); ?>
	</header>

	<div class="page-content">
		<?php the_content(); ?>
	</div>
</article>