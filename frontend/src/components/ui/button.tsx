import { cva, type VariantProps } from 'class-variance-authority'
import type { ButtonHTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center whitespace-nowrap rounded-control text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-fg focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-accent px-4 py-2 text-white hover:bg-accent/90',
        destructive: 'bg-danger px-4 py-2 text-white hover:bg-danger/90',
        outline: 'border border-border bg-transparent px-4 py-2 hover:bg-surface',
        secondary: 'bg-surface px-4 py-2 text-foreground hover:bg-surface/80',
        ghost: 'px-3 py-2 hover:bg-surface',
        link: 'text-accent-fg underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-10',
        sm: 'h-9 rounded-control px-3',
        lg: 'h-11 rounded-control px-8',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

export type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & VariantProps<typeof buttonVariants>

export function Button({ className, variant, size, ...props }: ButtonProps) {
  return <button className={cn(buttonVariants({ variant, size }), className)} {...props} />
}
