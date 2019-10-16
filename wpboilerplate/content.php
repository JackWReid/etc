<?php
/**
 * @package boilerplate
 */
?>

<article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
	<header class="post-header">
		<?php the_title( sprintf( '<h1 class="post-title"><a href="%s" rel="bookmark">', esc_url( get_permalink() ) ), '</a></h1>' ); ?>
	</header>

	<div class="post-content">
		<?php the_content() ); ?>
	</div>

</article>
