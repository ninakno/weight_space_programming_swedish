# Arm C edit iterations

Every candidate edit evaluated on the dev set, in order.

## 2026-11-19 16:19  `none`  (split=design)


embedded acc=0.916  main acc=0.771

```
                        n    acc  margin
clause   adverb_group                   
embedded dev_only      66  0.970   4.929
         shared        88  0.875   3.847
main     dev_only      54  0.815  -0.027
         shared        86  0.744  -0.406
```

## 2026-11-19 16:20  `h25.3+4_x1.5`  (split=design)

- {'param': 'model.layers.25.self_attn.o_proj.weight', 'kind': 'cols', 'n_index': 64, 'norm': 25.24725, 'note': 'scale head 25.3 x1.5'}
- {'param': 'model.layers.25.self_attn.o_proj.weight', 'kind': 'cols', 'n_index': 64, 'norm': 17.259598, 'note': 'scale head 25.4 x1.5'}

embedded acc=0.916  main acc=0.793

```
                        n    acc  margin
clause   adverb_group                   
embedded dev_only      66  0.970   5.622
         shared        88  0.875   4.388
main     dev_only      54  0.833  -0.012
         shared        86  0.767  -0.371
```

## 2026-11-19 16:21  `h25.3+4_x2`  (split=design)

- {'param': 'model.layers.25.self_attn.o_proj.weight', 'kind': 'cols', 'n_index': 64, 'norm': 50.494499, 'note': 'scale head 25.3 x2.0'}
- {'param': 'model.layers.25.self_attn.o_proj.weight', 'kind': 'cols', 'n_index': 64, 'norm': 34.519199, 'note': 'scale head 25.4 x2.0'}

embedded acc=0.922  main acc=0.807

```
                        n    acc  margin
clause   adverb_group                   
embedded dev_only      66  0.970   6.169
         shared        88  0.886   4.804
main     dev_only      54  0.833   0.007
         shared        86  0.791  -0.345
```

## 2026-11-19 16:22  `h25.3+4_x3`  (split=design)

- {'param': 'model.layers.25.self_attn.o_proj.weight', 'kind': 'cols', 'n_index': 64, 'norm': 100.988998, 'note': 'scale head 25.3 x3.0'}
- {'param': 'model.layers.25.self_attn.o_proj.weight', 'kind': 'cols', 'n_index': 64, 'norm': 69.038399, 'note': 'scale head 25.4 x3.0'}

embedded acc=0.929  main acc=0.821

```
                        n    acc  margin
clause   adverb_group                   
embedded dev_only      66  0.970   6.940
         shared        88  0.898   5.398
main     dev_only      54  0.852   0.058
         shared        86  0.802  -0.317
```

## 2026-11-19 16:45  `h13.5_x1.5`  (split=design)

- {'param': 'model.layers.13.self_attn.o_proj.weight', 'kind': 'cols', 'n_index': 64, 'norm': 15.416644, 'note': 'scale head 13.5 x1.5'}

embedded acc=0.935  main acc=0.779

```
                        n    acc  margin
clause   adverb_group                   
embedded dev_only      66  0.985   4.975
         shared        88  0.898   3.848
main     dev_only      54  0.815  -0.035
         shared        86  0.756  -0.414
```

## 2026-11-19 16:46  `h13.5_x2`  (split=design)

- {'param': 'model.layers.13.self_attn.o_proj.weight', 'kind': 'cols', 'n_index': 64, 'norm': 30.833288, 'note': 'scale head 13.5 x2.0'}

embedded acc=0.942  main acc=0.786

```
                        n    acc  margin
clause   adverb_group                   
embedded dev_only      66  0.985   4.973
         shared        88  0.909   3.826
main     dev_only      54  0.833  -0.040
         shared        86  0.756  -0.420
```

## 2026-11-19 16:47  `h13.5_x3`  (split=design)

- {'param': 'model.layers.13.self_attn.o_proj.weight', 'kind': 'cols', 'n_index': 64, 'norm': 61.666576, 'note': 'scale head 13.5 x3.0'}

embedded acc=0.961  main acc=0.793

```
                        n    acc  margin
clause   adverb_group                   
embedded dev_only      66  0.985   4.900
         shared        88  0.943   3.722
main     dev_only      54  0.833  -0.046
         shared        86  0.767  -0.428
```

## 2026-11-19 16:48  `h13.5_x2+h25.3+4_x2`  (split=design)

- {'param': 'model.layers.13.self_attn.o_proj.weight', 'kind': 'cols', 'n_index': 64, 'norm': 30.833288, 'note': 'scale head 13.5 x2.0'}
- {'param': 'model.layers.25.self_attn.o_proj.weight', 'kind': 'cols', 'n_index': 64, 'norm': 50.494499, 'note': 'scale head 25.3 x2.0'}
- {'param': 'model.layers.25.self_attn.o_proj.weight', 'kind': 'cols', 'n_index': 64, 'norm': 34.519196, 'note': 'scale head 25.4 x2.0'}

embedded acc=0.974  main acc=0.800

```
                        n    acc  margin
clause   adverb_group                   
embedded dev_only      66  0.985   6.204
         shared        88  0.966   4.775
main     dev_only      54  0.852  -0.005
         shared        86  0.767  -0.354
```

## 2026-11-19 16:50  `h13.5_x3+h25.3+4_x2`  (split=design)

- {'param': 'model.layers.13.self_attn.o_proj.weight', 'kind': 'cols', 'n_index': 64, 'norm': 61.666576, 'note': 'scale head 13.5 x3.0'}
- {'param': 'model.layers.25.self_attn.o_proj.weight', 'kind': 'cols', 'n_index': 64, 'norm': 50.494499, 'note': 'scale head 25.3 x2.0'}
- {'param': 'model.layers.25.self_attn.o_proj.weight', 'kind': 'cols', 'n_index': 64, 'norm': 34.519196, 'note': 'scale head 25.4 x2.0'}

embedded acc=0.974  main acc=0.807

```
                        n    acc  margin
clause   adverb_group                   
embedded dev_only      66  0.985   6.114
         shared        88  0.966   4.663
main     dev_only      54  0.852  -0.012
         shared        86  0.779  -0.359
```

## 2026-11-19 16:51  `h13.5_x3+h25.3+4_x3`  (split=design)

- {'param': 'model.layers.13.self_attn.o_proj.weight', 'kind': 'cols', 'n_index': 64, 'norm': 61.666576, 'note': 'scale head 13.5 x3.0'}
- {'param': 'model.layers.25.self_attn.o_proj.weight', 'kind': 'cols', 'n_index': 64, 'norm': 100.988998, 'note': 'scale head 25.3 x3.0'}
- {'param': 'model.layers.25.self_attn.o_proj.weight', 'kind': 'cols', 'n_index': 64, 'norm': 69.038391, 'note': 'scale head 25.4 x3.0'}

embedded acc=0.974  main acc=0.829

```
                        n    acc  margin
clause   adverb_group                   
embedded dev_only      66  0.985   6.868
         shared        88  0.966   5.252
main     dev_only      54  0.852   0.039
         shared        86  0.814  -0.331
```

## 2026-11-19 16:54  `none`  (split=check)


embedded acc=0.918  main acc=0.744

```
                        n    acc  margin
clause   adverb_group                   
embedded dev_only      64  0.938   4.888
         shared        82  0.902   3.335
main     dev_only      76  0.658   1.157
         shared        84  0.821  -0.266
```

## 2026-11-19 16:55  `h13.5_x2+h25.3+4_x2`  (split=check)

- {'param': 'model.layers.13.self_attn.o_proj.weight', 'kind': 'cols', 'n_index': 64, 'norm': 30.833288, 'note': 'scale head 13.5 x2.0'}
- {'param': 'model.layers.25.self_attn.o_proj.weight', 'kind': 'cols', 'n_index': 64, 'norm': 50.494499, 'note': 'scale head 25.3 x2.0'}
- {'param': 'model.layers.25.self_attn.o_proj.weight', 'kind': 'cols', 'n_index': 64, 'norm': 34.519196, 'note': 'scale head 25.4 x2.0'}

embedded acc=0.966  main acc=0.806

```
                        n    acc  margin
clause   adverb_group                   
embedded dev_only      64  0.969   5.918
         shared        82  0.963   4.371
main     dev_only      76  0.763   1.193
         shared        84  0.845  -0.183
```
