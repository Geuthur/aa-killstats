// Third Party
import {
    ShieldAlert,
    Factory,
    Truck,
    Radar,
    GraduationCap,
    CircuitBoard,
    CheckCircle2,
    Shield,
    MapPin,
    Users,
    Calendar,
    Radio,
    ExternalLink,
    Award,
    MessageSquare,
} from 'lucide-react';

interface IconProps {
    name: string;
    size?: number;
    className?: string;
}

const getIcon = ({
    name,
    size = 6,
    className: className = "text-zinc-400",
}: IconProps) => {
    switch (name) {
        case 'MessageSquare': return <MessageSquare className={`h-${size} w-${size} ${className}`} />;
        case 'Award': return <Award className={`h-${size} w-${size} ${className}`} />;
        case 'ShieldAlert': return <ShieldAlert className={`h-${size} w-${size} ${className}`} />;
        case 'Factory': return <Factory className={`h-${size} w-${size} ${className}`} />;
        case 'Truck': return <Truck className={`h-${size} w-${size} ${className}`} />;
        case 'Radar': return <Radar className={`h-${size} w-${size} ${className}`} />;
        case 'CircuitBoard': return <CircuitBoard className={`h-${size} w-${size} ${className}`} />;
        case 'CheckCircle2': return <CheckCircle2 className={`h-${size} w-${size} ${className}`} />;
        case 'Shield': return <Shield className={`h-${size} w-${size} ${className}`} />;
        case 'MapPin': return <MapPin className={`h-${size} w-${size} text-amber-400 ${className}`} />;
        case 'Users': return <Users className={`h-${size} w-${size} text-emerald-400 ${className}`} />;
        case 'Calendar': return <Calendar className={`h-${size} w-${size} text-emerald-400 ${className}`} />;
        case 'Radio': return <Radio className={`h-${size} w-${size} text-amber-400 ${className}`} />;
        case 'GraduationCap': return <GraduationCap className={`h-${size} w-${size} ${className}`} />;
        case 'ExternalLink': return <ExternalLink className={`h-${size} w-${size} ${className}`} />;
        default: return <GraduationCap className={`h-${size} w-${size} text-purple-400 ${className}`} />;
    }
};

export default getIcon;