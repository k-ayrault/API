<?php

namespace App\Processor;

use ApiPlatform\State\ProcessorInterface;
use ApiPlatform\Metadata\Operation;
use Symfony\Component\PasswordHasher\Hasher\UserPasswordHasherInterface;

class UserProcessor implements ProcessorInterface {

    private $userPasswordHasherInterface;
    
    public function __construct(UserPasswordHasherInterface $userPasswordHasherInterface)
    {  
        $this->userPasswordHasherInterface = $userPasswordHasherInterface;
    }
    
    public function process($user, Operation $operation, array $uriVariables = [], array $context = [])
    {
        if ($user->getPassword()) {
            $user->setPassword(
                $this->userPasswordEncoder->encodePassword($user, $user->getPassword())
            );
        }
        
        return $user;
    }
} 

?>