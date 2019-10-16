<?php
/**
 * The template for displaying archive pages.
 *
 * Learn more: http://codex.wordpress.org/Template_Hierarchy
 *
 * @package boilerplate
 */

get_header(); ?>

<main id="main" role="main">

<?php if ( have_posts() ) : ?>

	<header class="page-header">
		<h1 class="page-title">
			<?php
				if ( is_category() ) :
					single_cat_title();

				elseif ( is_tag() ) :
					single_tag_title();

				endif;
			?>
		</h1>
	</header>

	<?php while ( have_posts() ) : the_post(); ?>

		<?php
			get_template_part( 'content', get_post_format() );
		?>

	<?php endwhile; ?>

<?php else : ?>

	<?php get_template_part( 'content', 'none' ); ?>

<?php endif; ?>

</main>

<?php get_sidebar(); ?>
<?php get_footer(); ?>
