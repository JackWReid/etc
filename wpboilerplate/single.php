<?php
/**
 * The template for displaying all single posts.
 *
 * @package boilerplate
 */

get_header(); ?>

<main role="main">

<?php while ( have_posts() ) : the_post(); ?>

	<?php get_template_part( 'content', 'single' ); ?>

	<?php
		if ( comments_open() || '0' != get_comments_number() ) :
			comments_template();
		endif;
	?>

<?php endwhile; ?>

</main>

<?php get_sidebar(); ?>
<?php get_footer(); ?>