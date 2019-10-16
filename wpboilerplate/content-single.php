<?php
/**
 * @package boilerplate
 */
?>

<article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>

	<header class="post-header">
		<?php the_title( '<h1 class="post-title">', '</h1>' ); ?>
	</header>

	<div class="post-content">
		<?php the_content(); ?>
	</div>

</article>
